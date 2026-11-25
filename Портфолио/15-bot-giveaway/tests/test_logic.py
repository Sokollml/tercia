"""Unit tests for the pure business logic (no aiogram / DB needed)."""

from __future__ import annotations

import pytest

from bot import logic


# --------------------------------------------------------------------------
# Deterministic winner selection: same seed + participants => same winners.
# --------------------------------------------------------------------------
def test_select_winners_is_reproducible_for_same_seed():
    participants = [(uid, 1) for uid in range(1, 101)]
    seed = "deadbeefcafe"

    first = logic.select_winners(participants, seed, winners_count=3)
    second = logic.select_winners(participants, seed, winners_count=3)

    assert first == second
    assert len(first) == 3
    assert len(set(first)) == 3  # unique winners


def test_select_winners_order_independent():
    """Row order from the DB must not change the outcome."""
    participants = [(uid, 1) for uid in range(1, 51)]
    seed = "seed-xyz"

    normal = logic.select_winners(participants, seed, winners_count=5)
    shuffled = logic.select_winners(list(reversed(participants)), seed, winners_count=5)

    assert normal == shuffled


def test_different_seed_generally_changes_winners():
    participants = [(uid, 1) for uid in range(1, 201)]
    a = logic.select_winners(participants, "seed-a", winners_count=5)
    b = logic.select_winners(participants, "seed-b", winners_count=5)
    assert a != b


def test_verify_draw_roundtrip():
    participants = [(uid, uid % 4 + 1) for uid in range(1, 60)]
    seed = "verify-me"
    winners = logic.select_winners(participants, seed, winners_count=4)

    assert logic.verify_draw(participants, seed, 4, winners) is True
    # Order should not matter for verification.
    assert logic.verify_draw(participants, seed, 4, list(reversed(winners))) is True
    # A tampered winner list must fail verification.
    assert logic.verify_draw(participants, seed, 4, winners[:-1] + [999999]) is False


def test_select_winners_empty_pool():
    assert logic.select_winners([], "seed", winners_count=3) == []
    # Zero-ticket entries are dropped.
    assert logic.select_winners([(1, 0), (2, 0)], "seed", winners_count=1) == []


def test_select_winners_more_than_pool():
    participants = [(1, 1), (2, 1)]
    winners = logic.select_winners(participants, "seed", winners_count=5)
    assert set(winners) == {1, 2}


def test_weight_bias_favours_high_ticket_users():
    """Over many seeds, a heavily weighted user should win far more often."""
    heavy = 1
    light_ids = list(range(2, 12))  # 10 light users
    wins_heavy = 0
    trials = 300
    for i in range(trials):
        pool = [(heavy, 100)] + [(uid, 1) for uid in light_ids]
        winner = logic.select_winners(pool, f"seed-{i}", winners_count=1)[0]
        if winner == heavy:
            wins_heavy += 1
    # With weight 100 vs 10*1, the heavy user should dominate.
    assert wins_heavy > trials * 0.7


# --------------------------------------------------------------------------
# Tickets calculation.
# --------------------------------------------------------------------------
def test_compute_tickets_basic():
    assert logic.compute_tickets(1, 0, 1) == 1
    assert logic.compute_tickets(1, 3, 1) == 4
    assert logic.compute_tickets(1, 2, 5) == 11


def test_compute_tickets_floor_is_one():
    assert logic.compute_tickets(0, 0, 0) == 1


def test_compute_tickets_rejects_negatives():
    with pytest.raises(ValueError):
        logic.compute_tickets(-1, 0, 1)
    with pytest.raises(ValueError):
        logic.compute_tickets(1, -1, 1)


# --------------------------------------------------------------------------
# Referral counting (anti-abuse: dedupe + no self-referral).
# --------------------------------------------------------------------------
def test_count_referrals_dedupes_and_ignores_self():
    rows = [
        {"inviter_id": 10, "invited_id": 20},
        {"inviter_id": 10, "invited_id": 20},  # duplicate -> counted once
        {"inviter_id": 10, "invited_id": 30},
        {"inviter_id": 10, "invited_id": 10},  # self -> ignored
        {"inviter_id": 99, "invited_id": 40},  # other inviter -> ignored
    ]
    assert logic.count_referrals(rows, 10) == 2
    assert logic.count_referrals(rows, 99) == 1
    assert logic.count_referrals(rows, 12345) == 0


# --------------------------------------------------------------------------
# Deep-link payload parsing / building.
# --------------------------------------------------------------------------
def test_parse_start_payload_variants():
    assert logic.parse_start_payload("g42") == {"giveaway_id": 42}
    assert logic.parse_start_payload("g42_r777") == {"giveaway_id": 42, "referrer_id": 777}
    assert logic.parse_start_payload("ref555") == {"referrer_id": 555}
    assert logic.parse_start_payload("") == {}
    assert logic.parse_start_payload("garbage") == {}


def test_build_and_parse_roundtrip():
    payload = logic.build_start_payload(7, 12345)
    assert payload == "g7_r12345"
    assert logic.parse_start_payload(payload) == {"giveaway_id": 7, "referrer_id": 12345}


def test_generate_seed_is_unique_and_hex():
    a = logic.generate_seed()
    b = logic.generate_seed()
    assert a != b
    assert len(a) == 64
    int(a, 16)  # valid hex
