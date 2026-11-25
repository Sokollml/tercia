"""Tests for the pure LLM-reply parsing (app.llm.extract_correction)."""
from __future__ import annotations

from app.llm import Correction, build_messages, extract_correction


def test_clean_json_object():
    raw = (
        '{"has_errors": true, "corrected": "I have been", '
        '"explanation": "use present perfect", "error_type": "tense", '
        '"reply": "Nice, tell me more!"}'
    )
    c = extract_correction(raw)
    assert c.has_errors is True
    assert c.corrected == "I have been"
    assert c.error_type == "tense"
    assert c.reply == "Nice, tell me more!"


def test_json_wrapped_in_code_fence():
    raw = "```json\n{\"has_errors\": false, \"reply\": \"Great!\"}\n```"
    c = extract_correction(raw)
    assert c.has_errors is False
    assert c.reply == "Great!"


def test_json_with_surrounding_prose():
    raw = 'Sure! Here you go: {"has_errors": false, "reply": "ok"} hope that helps'
    c = extract_correction(raw)
    assert c.reply == "ok"


def test_garbage_falls_back_to_reply_text():
    c = extract_correction("just some plain prose, no json here", fallback_reply="fb")
    assert c.has_errors is False
    # The plain prose becomes the conversational reply.
    assert "plain prose" in c.reply


def test_invalid_json_uses_fallback():
    c = extract_correction("{not: valid json,,,}", fallback_reply="fallback")
    assert c.has_errors is False
    assert c.reply  # non-empty


def test_empty_input_uses_fallback_reply():
    c = extract_correction("", fallback_reply="hi there")
    assert c.reply == "hi there"
    assert c.has_errors is False


def test_unknown_error_type_normalised_to_other():
    raw = '{"has_errors": true, "corrected": "x", "error_type": "made_up_type"}'
    c = extract_correction(raw)
    assert c.error_type == "other"


def test_mistakes_array_drives_has_errors_and_fills_top_level():
    raw = (
        '{"has_errors": false, "mistakes": [{"original": "i go", '
        '"corrected": "I went", "explanation": "past tense", '
        '"error_type": "tense"}]}'
    )
    c = extract_correction(raw)
    # mistakes present -> has_errors becomes True regardless of the flag.
    assert c.has_errors is True
    assert c.corrected == "I went"
    assert c.error_type == "tense"
    assert len(c.mistakes) == 1


def test_braces_inside_strings_do_not_break_scan():
    raw = '{"has_errors": false, "reply": "use {curly} braces carefully"}'
    c = extract_correction(raw)
    assert c.reply == "use {curly} braces carefully"


def test_string_boolean_coercion():
    raw = '{"has_errors": "true", "corrected": "ok"}'
    c = extract_correction(raw)
    assert c.has_errors is True


def test_build_messages_shape():
    msgs = build_messages("Hallo", "German", "A2", "ru")
    assert msgs[0]["role"] == "system"
    assert "German" in msgs[0]["content"]
    assert msgs[-1] == {"role": "user", "content": "Hallo"}


def test_build_messages_truncates_history():
    history = [{"role": "user", "content": str(i)} for i in range(20)]
    msgs = build_messages("now", "English", "B1", "en", history=history)
    # system + up to 6 history + current user message
    assert len(msgs) <= 1 + 6 + 1


def test_to_public_keys():
    pub = Correction(has_errors=True, corrected="x").to_public()
    assert set(pub) == {"has_errors", "corrected", "explanation", "error_type", "reply"}
