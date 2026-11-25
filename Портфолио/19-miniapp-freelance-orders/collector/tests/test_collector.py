"""Тесты сборщика с МОКОМ Telegram (реального подключения нет).

Подменяем клиента Telethon фейком с async-генератором iter_messages,
проверяем, что fetch_new_messages корректно собирает RawMessage.
"""

import asyncio

import collector


class FakeSender:
    def __init__(self, username):
        self.username = username


class FakeMessage:
    def __init__(self, mid, text, username=None):
        self.id = mid
        self.message = text
        self._sender = FakeSender(username) if username else None

    async def get_sender(self):
        return self._sender


class FakeClient:
    """Мок Telethon-клиента. Отдаёт заранее заданные сообщения."""

    def __init__(self, messages):
        self._messages = messages
        self.calls = []

    def iter_messages(self, chat, min_id=0, limit=100):
        self.calls.append((chat, min_id, limit))

        async def gen():
            for m in self._messages:
                if m.id > min_id:
                    yield m

        return gen()


def test_fetch_new_messages_builds_records():
    client = FakeClient(
        [
            FakeMessage(1, "Ищу дизайнера", username="alice"),
            FakeMessage(2, "", username="bob"),  # пустое -> пропустить
            FakeMessage(3, "Нужен разработчик", username=None),
        ]
    )
    result = asyncio.run(
        collector.fetch_new_messages(client, "@chat", min_id=0)
    )
    assert len(result) == 2
    assert result[0].author == "alice"
    assert result[0].text == "Ищу дизайнера"
    assert result[1].author is None  # sender без username
    assert result[1].message_id == 3


def test_fetch_respects_min_id():
    client = FakeClient(
        [FakeMessage(5, "старое"), FakeMessage(10, "новое")]
    )
    result = asyncio.run(
        collector.fetch_new_messages(client, "@chat", min_id=5)
    )
    assert len(result) == 1
    assert result[0].message_id == 10
