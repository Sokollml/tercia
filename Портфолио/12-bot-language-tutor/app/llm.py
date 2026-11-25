"""LLM integration for an OpenAI-compatible chat/completions endpoint.

Two responsibilities live here:

1. :func:`extract_correction` — *pure* parsing of a model reply into a strict
   :class:`Correction`.  Models are unreliable at emitting clean JSON, so this
   strips code fences, isolates the first balanced ``{...}`` object and falls
   back to a safe "no correction" result on garbage.  This function has no I/O
   and is fully unit-tested.

2. :class:`LLMClient` — a thin async HTTP wrapper (aiohttp) that builds the
   prompt, calls the endpoint and delegates parsing to the pure helpers.

The network client is imported lazily so this module (and the whole app) can be
imported in tests without aiohttp making any calls.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

log = logging.getLogger("tutor.llm")

# Error-type taxonomy the model is asked to use; anything else is normalised to
# "other" so downstream code and quizzes can rely on a closed set.
ERROR_TYPES = {
    "grammar",
    "vocabulary",
    "spelling",
    "word_order",
    "punctuation",
    "article",
    "preposition",
    "tense",
    "agreement",
    "style",
    "other",
}


@dataclass
class Correction:
    """Structured result of analysing one user message."""

    has_errors: bool = False
    corrected: str = ""       # the corrected sentence (or the original if clean)
    explanation: str = ""     # short, learner-facing explanation
    error_type: str = "other"
    reply: str = ""           # the tutor's conversational reply in the target lang
    mistakes: List[Dict[str, str]] = field(default_factory=list)

    def to_public(self) -> Dict[str, Any]:
        return {
            "has_errors": self.has_errors,
            "corrected": self.corrected,
            "explanation": self.explanation,
            "error_type": self.error_type,
            "reply": self.reply,
        }


def _strip_code_fences(text: str) -> str:
    """Remove Markdown code fences the model may wrap JSON in."""
    t = text.strip()
    if t.startswith("```"):
        # drop the opening fence (``` or ```json) and the trailing fence
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1 :]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[: -3]
    return t.strip()


def _first_json_object(text: str) -> Optional[str]:
    """Return the first balanced ``{...}`` substring, or ``None``.

    Brace-aware and string-aware so braces inside JSON string values do not
    confuse the scan.
    """
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "да"}
    return bool(value)


def _normalise_error_type(value: Any) -> str:
    if isinstance(value, str) and value.strip().lower() in ERROR_TYPES:
        return value.strip().lower()
    return "other"


def _normalise_mistakes(raw: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "original": str(item.get("original", "") or ""),
                "corrected": str(item.get("corrected", "") or ""),
                "explanation": str(item.get("explanation", "") or ""),
                "error_type": _normalise_error_type(item.get("error_type")),
            }
        )
    return out


def extract_correction(raw_reply: str, fallback_reply: str = "") -> Correction:
    """Parse a raw model reply into a :class:`Correction`, never raising.

    On any parsing failure it returns a benign "no errors" correction whose
    ``reply`` is either the model's plain text (trimmed) or ``fallback_reply``.
    """
    if not raw_reply or not raw_reply.strip():
        return Correction(reply=fallback_reply)

    candidate = _first_json_object(_strip_code_fences(raw_reply))
    if candidate is None:
        # Model answered in prose; treat the whole thing as a conversational reply.
        return Correction(reply=raw_reply.strip() or fallback_reply)

    try:
        data = json.loads(candidate)
    except (ValueError, TypeError):
        log.warning("LLM returned non-JSON payload; using fallback")
        return Correction(reply=raw_reply.strip() or fallback_reply)

    if not isinstance(data, dict):
        return Correction(reply=fallback_reply)

    mistakes = _normalise_mistakes(data.get("mistakes"))
    has_errors = _coerce_bool(data.get("has_errors")) or bool(mistakes)

    # Prefer the top-level fields, but fall back to the first mistake entry.
    corrected = str(data.get("corrected", "") or "")
    explanation = str(data.get("explanation", "") or "")
    error_type = _normalise_error_type(data.get("error_type"))
    if not corrected and mistakes:
        corrected = mistakes[0]["corrected"]
    if not explanation and mistakes:
        explanation = mistakes[0]["explanation"]
    if error_type == "other" and mistakes:
        error_type = mistakes[0]["error_type"]

    reply = str(data.get("reply", "") or "").strip() or fallback_reply

    return Correction(
        has_errors=has_errors,
        corrected=corrected,
        explanation=explanation,
        error_type=error_type,
        reply=reply,
        mistakes=mistakes,
    )


# --- Prompt construction (pure) ------------------------------------------

_SYSTEM_TEMPLATE = (
    "You are a friendly, patient language tutor. The student is learning "
    "{language} at CEFR level {level}. Always reply in {language}, adapting your "
    "vocabulary to their level.\n\n"
    "Analyse the student's latest message for language mistakes. Then respond "
    "with ONLY a single JSON object (no markdown, no prose outside JSON) using "
    "exactly this schema:\n"
    "{{\n"
    '  "has_errors": boolean,\n'
    '  "corrected": "the fully corrected version of their message",\n'
    '  "explanation": "a short, gentle explanation in {ui_language}",\n'
    '  "error_type": one of ["grammar","vocabulary","spelling","word_order",'
    '"punctuation","article","preposition","tense","agreement","style","other"],\n'
    '  "mistakes": [ {{"original": "...", "corrected": "...", '
    '"explanation": "...", "error_type": "..."}} ],\n'
    '  "reply": "your natural conversational reply in {language} that keeps the '
    "conversation going\"\n"
    "}}\n\n"
    "If the message is already correct, set has_errors=false, echo it in "
    "corrected, leave mistakes empty, and still provide a warm reply."
)

UI_LANGUAGE_NAMES = {"ru": "Russian", "en": "English"}


def build_messages(
    user_text: str,
    learn_language: str,
    level: str,
    ui_lang: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """Assemble the chat messages for a dialog-mode analysis call."""
    system = _SYSTEM_TEMPLATE.format(
        language=learn_language,
        level=level,
        ui_language=UI_LANGUAGE_NAMES.get(ui_lang, "English"),
    )
    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_text})
    return messages


class LLMError(Exception):
    """Raised when the LLM endpoint cannot be reached or returns an error."""


class LLMClient:
    """Async client for an OpenAI-compatible ``/chat/completions`` endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def _raw_complete(self, messages: List[Dict[str, str]]) -> str:
        # Imported lazily so importing this module never requires aiohttp.
        import aiohttp

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        raise LLMError(f"LLM HTTP {resp.status}: {body[:200]}")
                    data = await resp.json()
        except LLMError:
            raise
        except Exception as exc:  # network / json errors
            raise LLMError(str(exc)) from exc

        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"unexpected LLM response shape: {exc}") from exc

    async def analyse(
        self,
        user_text: str,
        learn_language: str,
        level: str,
        ui_lang: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Correction:
        """Analyse a message and return a parsed :class:`Correction`.

        Never raises for parsing issues; a network failure raises
        :class:`LLMError` so the handler can show a graceful notice.
        """
        messages = build_messages(user_text, learn_language, level, ui_lang, history)
        raw = await self._raw_complete(messages)
        return extract_correction(raw, fallback_reply=user_text)

    async def make_quiz_prompt(
        self, mistake: Dict[str, Any], learn_language: str, ui_lang: str
    ) -> str:
        """Build a fill-in-the-blank style question string from a stored mistake.

        This is deliberately local (no network) so quizzes work even if the LLM
        is temporarily unavailable; the stored ``corrected``/``original`` pair is
        enough to quiz the learner.
        """
        return mistake.get("corrected", "") or mistake.get("original", "")
