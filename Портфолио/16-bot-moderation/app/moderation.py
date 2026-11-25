"""Pure moderation logic — no I/O, no aiogram, no DB.

Everything here is deterministic and unit-tested.  Handlers call these helpers
and then perform the side effects (send message, restrict user, write to DB).
"""
from __future__ import annotations

import random
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Sequence, Tuple


def now_ts() -> int:
    """Current UNIX time in seconds (UTC)."""
    return int(time.time())


# --------------------------------------------------------------------------- #
# Warnings -> mute escalation
# --------------------------------------------------------------------------- #
def should_mute(active_warns: int, warn_limit: int) -> bool:
    """Return True when the number of active warnings reaches the limit.

    ``warn_limit <= 0`` disables auto-mute entirely.
    """
    if warn_limit <= 0:
        return False
    return active_warns >= warn_limit


# --------------------------------------------------------------------------- #
# Captcha
# --------------------------------------------------------------------------- #
@dataclass
class Captcha:
    """A tiny arithmetic captcha with multiple-choice answers."""

    question: str          # e.g. "3 + 4 = ?"
    answer: str            # correct token, e.g. "7"
    options: List[str]     # shuffled tokens shown as buttons


def make_captcha(rng: Optional[random.Random] = None) -> Captcha:
    """Build a simple ``a + b`` captcha with three answer options.

    ``rng`` is injectable so tests are deterministic.
    """
    r = rng or random
    a = r.randint(1, 9)
    b = r.randint(1, 9)
    correct = a + b
    # Two plausible distractors near the correct value.
    distractors: set = set()
    while len(distractors) < 2:
        delta = r.randint(-3, 3)
        cand = correct + delta
        if cand != correct and cand > 0:
            distractors.add(cand)
    options = [str(correct)] + [str(d) for d in distractors]
    r.shuffle(options)
    return Captcha(question="%d + %d = ?" % (a, b), answer=str(correct), options=options)


def check_captcha(expected: str, given: str) -> bool:
    """Constant-ish comparison of the captcha token."""
    return str(expected).strip() == str(given).strip()


def is_expired(deadline_ts: int, now: Optional[int] = None) -> bool:
    """Whether a captcha deadline has passed (-> the user should be kicked)."""
    current = now_ts() if now is None else now
    return current >= deadline_ts


# --------------------------------------------------------------------------- #
# Antispam filters
# --------------------------------------------------------------------------- #
_URL_RE = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|@[A-Za-z0-9_]{5,}|\b\S+\.(?:com|ru|net|org|io|me|xyz|top|link)\b)",
    re.IGNORECASE,
)


def has_link(text: str) -> bool:
    """Heuristic link / username / mention detector for newcomer messages."""
    if not text:
        return False
    return bool(_URL_RE.search(text))


def _normalize(text: str) -> str:
    return (text or "").lower()


def parse_stopwords(raw: str) -> List[str]:
    """Split the stored comma-separated stop-word list into normalized tokens."""
    out: List[str] = []
    for chunk in (raw or "").split(","):
        chunk = chunk.strip().lower()
        if chunk:
            out.append(chunk)
    return out


def matched_stopword(text: str, stopwords: Sequence[str]) -> Optional[str]:
    """Return the first stop-word contained in ``text`` (or None).

    Matching is case-insensitive substring; a whole-word match is preferred but
    substring keeps it simple and catches obfuscation like ``spaaam``-free ads.
    """
    low = _normalize(text)
    if not low:
        return None
    for word in stopwords:
        if not word:
            continue
        # Word-boundary match when the stop-word is alphanumeric, else substring.
        if re.search(r"\w", word):
            if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", low):
                return word
        elif word in low:
            return word
    return None


# --------------------------------------------------------------------------- #
# Antiflood — sliding window per (chat, user)
# --------------------------------------------------------------------------- #
class FloodTracker:
    """In-memory sliding-window flood detector.

    ``limit`` messages allowed per ``window`` seconds; the message that crosses
    the limit trips it.
    """

    def __init__(self, limit: int = 5, window: int = 5) -> None:
        self.limit = max(1, limit)
        self.window = max(1, window)
        self._hits: Dict[Tuple[int, int], Deque[float]] = defaultdict(deque)

    def hit(self, chat_id: int, user_id: int, now: Optional[float] = None) -> bool:
        """Record a message; return True if the user is now flooding."""
        t = time.monotonic() if now is None else now
        key = (chat_id, user_id)
        hits = self._hits[key]
        while hits and t - hits[0] > self.window:
            hits.popleft()
        hits.append(t)
        return len(hits) > self.limit

    def reset(self, chat_id: int, user_id: int) -> None:
        self._hits.pop((chat_id, user_id), None)


def format_duration(seconds: int, lang: str = "ru") -> str:
    """Human-readable mute duration for log/notice messages."""
    if seconds <= 0:
        return "∞"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts: List[str] = []
    units = {
        "ru": ["д", "ч", "м", "с"],
        "en": ["d", "h", "m", "s"],
    }.get(lang, ["d", "h", "m", "s"])
    for value, unit in zip((d, h, m, s), units):
        if value:
            parts.append("%d%s" % (value, unit))
    return " ".join(parts) if parts else ("0" + units[-1])
