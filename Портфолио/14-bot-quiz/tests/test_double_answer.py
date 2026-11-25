"""Integration tests for answer recording, double-answer protection and scoring.

These exercise the real async repository against a temporary SQLite database.
"""
from __future__ import annotations

import pytest

from bot import db as repo


async def _make_quiz(database, *, season_id, correct_index=1):
    async with database.session() as session:
        question = await repo.add_question(
            session,
            category="Test",
            lang="ru",
            text="2 + 2 = ?",
            options=["3", "4", "5"],
            correct_index=correct_index,
        )
        quiz = await repo.create_quiz(
            session,
            poll_id="poll-123",
            chat_id=-100,
            message_id=1,
            question_id=question.id,
            season_id=season_id,
            mode="daily",
            correct_index=correct_index,
        )
        return quiz


@pytest.mark.asyncio
async def test_double_answer_is_rejected(database):
    async with database.session() as session:
        season = await repo.start_new_season(session, "S1")
    quiz = await _make_quiz(database, season_id=season.id)

    async with database.session() as session:
        quiz = await repo.get_quiz_by_poll(session, "poll-123")
        first = await repo.record_answer(
            session, quiz=quiz, user_id=42, username="alice",
            option_index=1, is_correct=True, points=10,
        )

    async with database.session() as session:
        quiz = await repo.get_quiz_by_poll(session, "poll-123")
        second = await repo.record_answer(
            session, quiz=quiz, user_id=42, username="alice",
            option_index=0, is_correct=False, points=0,
        )

    assert first is True
    assert second is False  # second answer for the same (poll, user) is ignored

    # Score reflects only the first answer.
    async with database.session() as session:
        score = await repo.get_user_score(session, season.id, 42)
    assert score is not None
    assert score.points == 10
    assert score.correct_count == 1
    assert score.total_count == 1


@pytest.mark.asyncio
async def test_scores_accumulate_across_users_and_polls(database):
    async with database.session() as session:
        season = await repo.start_new_season(session, "S1")

    # Two different polls, so the unique (poll, user) guard does not interfere.
    async with database.session() as session:
        q1 = await repo.add_question(
            session, category="T", lang="ru", text="q1",
            options=["a", "b"], correct_index=0,
        )
        quiz1 = await repo.create_quiz(
            session, poll_id="p1", chat_id=-1, message_id=1,
            question_id=q1.id, season_id=season.id, mode="daily", correct_index=0,
        )
        quiz2 = await repo.create_quiz(
            session, poll_id="p2", chat_id=-1, message_id=2,
            question_id=q1.id, season_id=season.id, mode="daily", correct_index=0,
        )

    async with database.session() as session:
        quiz1 = await repo.get_quiz_by_poll(session, "p1")
        await repo.record_answer(
            session, quiz=quiz1, user_id=1, username="alice",
            option_index=0, is_correct=True, points=12,
        )
    async with database.session() as session:
        quiz2 = await repo.get_quiz_by_poll(session, "p2")
        await repo.record_answer(
            session, quiz=quiz2, user_id=1, username="alice",
            option_index=1, is_correct=False, points=0,
        )
    async with database.session() as session:
        quiz1 = await repo.get_quiz_by_poll(session, "p1")
        await repo.record_answer(
            session, quiz=quiz1, user_id=2, username="bob",
            option_index=0, is_correct=True, points=10,
        )

    async with database.session() as session:
        alice = await repo.get_user_score(session, season.id, 1)
        board = await repo.get_leaderboard(session, season.id, limit=10)

    assert alice.points == 12
    assert alice.correct_count == 1
    assert alice.total_count == 2  # answered two polls, one correct
    # Leaderboard ordered by points desc: alice (12) before bob (10).
    assert [s.user_id for s in board] == [1, 2]


@pytest.mark.asyncio
async def test_answer_without_season_does_not_crash(database):
    # A quiz with no season (season_id=None) records the answer but skips scoring.
    quiz = await _make_quiz(database, season_id=None)
    async with database.session() as session:
        quiz = await repo.get_quiz_by_poll(session, "poll-123")
        stored = await repo.record_answer(
            session, quiz=quiz, user_id=7, username="carol",
            option_index=1, is_correct=True, points=10,
        )
    assert stored is True
