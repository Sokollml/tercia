"""Тесты парсинга ответа ИИ-классификатора + fallback."""

from classifier_parse import DEFAULT_RESULT, parse_classifier_output


def test_clean_json():
    raw = (
        '{"is_order": true, "service_type": "dev", "summary": "бот",'
        ' "budget": 15000, "urgency": "high", "languages": ["ru"],'
        ' "skills_required": ["python", "aiogram"]}'
    )
    r = parse_classifier_output(raw)
    assert r["is_order"] is True
    assert r["service_type"] == "dev"
    assert r["budget"] == 15000.0
    assert r["urgency"] == "high"
    assert r["languages"] == ["ru"]
    assert r["skills_required"] == ["python", "aiogram"]


def test_fenced_markdown_json():
    raw = "```json\n{\"is_order\": true, \"budget\": \"10 000 руб\"}\n```"
    r = parse_classifier_output(raw)
    assert r["is_order"] is True
    assert r["budget"] == 10000.0


def test_garbage_before_after():
    raw = "Вот ответ: {\"is_order\": false} — надеюсь помог"
    r = parse_classifier_output(raw)
    assert r["is_order"] is False


def test_invalid_json_returns_default():
    r = parse_classifier_output("это не json совсем")
    assert r == DEFAULT_RESULT
    assert r["is_order"] is False


def test_empty_returns_default():
    assert parse_classifier_output("") == DEFAULT_RESULT


def test_bad_urgency_falls_back_to_low():
    r = parse_classifier_output('{"is_order": true, "urgency": "очень срочно"}')
    assert r["urgency"] == "low"


def test_budget_range_string():
    r = parse_classifier_output('{"is_order": true, "budget": "договорная"}')
    assert r["budget"] is None


def test_skills_lowercased_and_stripped():
    r = parse_classifier_output(
        '{"is_order": true, "skills_required": ["  Figma  ", "React"]}'
    )
    assert r["skills_required"] == ["figma", "react"]


def test_string_languages_wrapped_to_list():
    r = parse_classifier_output('{"is_order": true, "languages": "en"}')
    assert r["languages"] == ["en"]


def test_null_service_type():
    r = parse_classifier_output('{"is_order": false, "service_type": "null"}')
    assert r["service_type"] is None
