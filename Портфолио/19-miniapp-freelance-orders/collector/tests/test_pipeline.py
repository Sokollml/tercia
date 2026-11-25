"""Тесты пайплайна: префильтр + дедуп + сборка записей (без Telegram/БД)."""

from pipeline import (
    RawMessage,
    build_message_link,
    filter_records,
    process_messages,
    to_record,
)


def _msg(text, mid=1, chat="@chat", author="user"):
    return RawMessage(chat=chat, author=author, text=text, message_id=mid)


def test_build_message_link_public():
    assert build_message_link("@mychat", 42) == "https://t.me/mychat/42"
    assert build_message_link("mychat", 42) == "https://t.me/mychat/42"


def test_build_message_link_bad_chat():
    assert build_message_link("", 42) is None
    assert build_message_link("-100123456", 42) is None


def test_to_record_sets_hash_and_link():
    rec = to_record(_msg("Нужен дизайнер лендинга", mid=7))
    assert rec.text_hash and len(rec.text_hash) == 64
    assert rec.message_link == "https://t.me/chat/7"


def test_filter_records_keeps_only_orders():
    msgs = [
        _msg("Ищу разработчика бота, бюджет 30000", mid=1),
        _msg("всем привет как дела", mid=2),  # отсеется префильтром
        _msg("Ищу работу, вот моё портфолио", mid=3),  # стоп-слово
    ]
    recs = filter_records(msgs)
    assert len(recs) == 1
    assert recs[0].message_link.endswith("/1")


def test_filter_records_dedup_within_batch():
    msgs = [
        _msg("Нужен монтажёр для рилсов", mid=1),
        _msg("Нужен, монтажёр!! для рилсов", mid=2),  # тот же хеш
    ]
    recs = filter_records(msgs)
    assert len(recs) == 1


def test_process_messages_stats_and_insert():
    inserted = []

    def on_record(rec):
        inserted.append(rec)
        return True

    msgs = [
        _msg("Ищу таргетолога, оплата сдельная", mid=1),
        _msg("Ищу таргетолога, оплата сдельная", mid=2),  # дубль -> не вставится
        _msg("оффтоп ниочем", mid=3),  # отсеется
    ]
    stats = process_messages(msgs, on_record=on_record)
    assert stats.seen == 3
    assert stats.filtered_out == 1
    assert stats.duplicates == 1
    assert stats.accepted == 1
    assert len(inserted) == 1


def test_process_messages_db_reports_duplicate():
    # on_record возвращает False -> считаем, что БД отсекла по UNIQUE
    def on_record(_rec):
        return False

    stats = process_messages([_msg("Нужен копирайтер срочно")], on_record=on_record)
    assert stats.accepted == 0
    assert stats.duplicates == 1
