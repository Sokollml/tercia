"""Тесты дедупа: одинаковые по смыслу тексты дают одинаковый хеш."""

from dedup import normalize_for_hash, text_hash


def test_identical_text_same_hash():
    assert text_hash("Нужен дизайнер") == text_hash("Нужен дизайнер")


def test_case_and_spaces_ignored():
    assert text_hash("Нужен  ДИЗАЙНЕР") == text_hash("нужен дизайнер")


def test_links_and_mentions_stripped():
    a = "Нужен бот @client_manager https://t.me/somechat/5"
    b = "Нужен бот"
    assert text_hash(a) == text_hash(b)


def test_punctuation_ignored():
    assert text_hash("Нужен, дизайнер!!!") == text_hash("Нужен дизайнер")


def test_different_text_different_hash():
    assert text_hash("Нужен дизайнер") != text_hash("Нужен разработчик")


def test_hash_is_hex_sha256():
    h = text_hash("что угодно")
    assert len(h) == 64
    int(h, 16)  # не бросит, если это hex


def test_normalize_none_safe():
    assert normalize_for_hash(None) == ""
