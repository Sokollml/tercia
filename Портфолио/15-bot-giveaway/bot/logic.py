"""Pure, deterministic business logic for the giveaway bot.

This module intentionally has **no** dependency on aiogram or the database
layer so that it can be unit-tested in isolation and reused anywhere.

Key ideas
---------
* Fair winner selection is **deterministic** given a stored ``seed`` and the
  set of participants. Anyone can re-run :func:`select_winners` with the same
  seed and participant list and obtain the same winners -> provable fairness.
* Weighted sampling without replacement uses the Efraimidis-Spirakis
  algorithm (a random key ``u ** (1 / weight)`` per item, take the top-k).
  Participants are always processed in a canonical order (sorted by user_id)
  so the RNG draw sequence is stable regardless of DB row order.
"""

from __future__ import annotations

import hashlib
import random
import secrets
from typing import Iterable, List, Sequence, Tuple

# A participant as consumed by the draw: (user_id, tickets)
Participant = Tuple[int, int]


def generate_seed() -> str:
    """Return a fresh cryptographically-strong seed as a hex string.

    Stored in the DB *before* the draw so the outcome can be verified later.
    """
    return secrets.token_hex(32)


def compute_tickets(base_tickets: int, referrals: int, points_per_referral: int) -> int:
    """How many tickets (chances) a participant holds.

    Every participant gets ``base_tickets`` for joining, plus
    ``points_per_referral`` extra tickets for each successfully invited friend.
    The result is always at least 1 so nobody is silently excluded.
    """
    if base_tickets < 0 or referrals < 0 or points_per_referral < 0:
        raise ValueError("ticket inputs must be non-negative")
    return max(1, base_tickets + referrals * points_per_referral)


def _seeded_rng(seed: str, salt: str = "") -> random.Random:
    """Build a deterministic RNG from a (possibly long) string seed.

    We hash ``seed + salt`` to 64 bits so the RNG is stable across Python
    versions and independent of ``hash()`` randomization.
    """
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def select_winners(
    participants: Sequence[Participant],
    seed: str,
    winners_count: int = 1,
) -> List[int]:
    """Deterministically pick ``winners_count`` unique winners.

    Parameters
    ----------
    participants:
        Iterable of ``(user_id, tickets)`` pairs. ``tickets`` weights the
        chance of winning. Order does not matter -> it is canonicalised.
    seed:
        The stored seed. Same seed + same participants => same winners.
    winners_count:
        How many distinct winners to draw.

    Returns
    -------
    A list of winning ``user_id`` values, in draw order (first drawn first).
    """
    if winners_count < 1:
        raise ValueError("winners_count must be >= 1")

    # Canonical order: sort by user_id, drop non-positive tickets.
    pool: List[Participant] = sorted(
        ((int(uid), int(t)) for uid, t in participants if int(t) > 0),
        key=lambda p: p[0],
    )
    if not pool:
        return []

    rng = _seeded_rng(seed, salt="draw")

    # Efraimidis-Spirakis: key = u ** (1 / weight); take largest keys.
    keyed = []
    for user_id, tickets in pool:
        u = rng.random()
        # u in (0,1]; guard against exactly 0 to avoid math domain issues.
        u = u if u > 0.0 else 1e-18
        key = u ** (1.0 / tickets)
        keyed.append((key, user_id))

    keyed.sort(key=lambda k: (k[0], k[1]), reverse=True)
    return [user_id for _key, user_id in keyed[:winners_count]]


def verify_draw(
    participants: Sequence[Participant],
    seed: str,
    winners_count: int,
    claimed_winners: Iterable[int],
) -> bool:
    """Recompute the draw and compare to ``claimed_winners`` (order-agnostic)."""
    recomputed = select_winners(participants, seed, winners_count)
    return set(recomputed) == set(int(w) for w in claimed_winners)


def count_referrals(referral_rows: Iterable[dict], inviter_id: int) -> int:
    """Count valid (non-self) referrals credited to ``inviter_id``.

    ``referral_rows`` are mappings with ``inviter_id`` and ``invited_id`` keys.
    Self-referrals are ignored as an anti-abuse guard.
    """
    seen = set()
    for row in referral_rows:
        if int(row["inviter_id"]) != int(inviter_id):
            continue
        invited = int(row["invited_id"])
        if invited == int(inviter_id):
            continue  # cannot invite yourself
        seen.add(invited)
    return len(seen)


def parse_start_payload(payload: str) -> dict:
    """Parse a ``/start`` deep-link payload.

    Supported forms::

        g<giveaway_id>            -> join giveaway, no referrer
        g<giveaway_id>_r<user_id> -> join giveaway, referred by <user_id>
        ref<user_id>              -> bare referral (no giveaway context)

    Returns a dict with optional ``giveaway_id`` and ``referrer_id`` keys.
    Unknown / empty payloads yield an empty dict.
    """
    result: dict = {}
    if not payload:
        return result
    payload = payload.strip()

    if payload.startswith("g"):
        body = payload[1:]
        ref_part = None
        if "_r" in body:
            body, ref_part = body.split("_r", 1)
        if body.isdigit():
            result["giveaway_id"] = int(body)
        if ref_part and ref_part.isdigit():
            result["referrer_id"] = int(ref_part)
    elif payload.startswith("ref"):
        body = payload[3:]
        if body.isdigit():
            result["referrer_id"] = int(body)
    return result


def build_start_payload(giveaway_id: int, referrer_id: int) -> str:
    """Build the deep-link payload a participant shares to invite friends."""
    return f"g{int(giveaway_id)}_r{int(referrer_id)}"
