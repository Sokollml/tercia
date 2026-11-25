"""Тесты префильтра: ключевые слова пропускают, стоп-слова режут."""

from prefilter import passes_prefilter


def test_keyword_order_passes():
    assert passes_prefilter("Ищу дизайнера для лендинга, бюджет 20000") is True


def test_stopword_blocks_even_with_keyword():
    # есть ключевое «ищу», но стоп-слово «ищу работу» => не заказ
    assert passes_prefilter("Ищу работу дизайнером, портфолио внутри") is False


def test_short_message_rejected():
    assert passes_prefilter("нужен") is False


def test_empty_and_none_rejected():
    assert passes_prefilter("") is False
    assert passes_prefilter(None) is False


def test_no_keyword_rejected():
    assert passes_prefilter("Всем привет, как дела в этом чате сегодня?") is False


def test_english_keyword_passes():
    assert passes_prefilter("Looking for a React developer, budget negotiable") is True


def test_resume_stopword_blocks():
    assert passes_prefilter("Предлагаю услуги монтажа видео, недорого и быстро") is False


def test_custom_keywords_override():
    # с кастомным набором ключей дефолтные не действуют
    assert passes_prefilter("нужен монтажёр срочно", keywords=["монтажёр"]) is True
    assert passes_prefilter("нужен копирайтер", keywords=["монтажёр"]) is False
