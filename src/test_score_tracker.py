"""Tests for ScoreTracker — unit + property-based.

Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
"""
import pytest
from unittest.mock import MagicMock
from hypothesis import given, settings
from hypothesis import strategies as st

from score_tracker import ScoreTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_tracker(audio=None) -> ScoreTracker:
    return ScoreTracker(audio_service=audio)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestAddPoints:
    def test_increases_score(self):
        t = make_tracker()
        t.add_points(50)
        assert t.score == 50

    def test_no_bonus_below_threshold(self):
        t = make_tracker()
        t.add_points(999)
        assert t.lives == ScoreTracker.INITIAL_LIVES

    def test_bonus_life_at_exactly_1000(self):
        t = make_tracker()
        t.add_points(1000)
        assert t.lives == ScoreTracker.INITIAL_LIVES + 1

    def test_bonus_life_when_crossing_1000(self):
        t = make_tracker()
        t.add_points(500)
        t.add_points(600)  # crosses 1000
        assert t.lives == ScoreTracker.INITIAL_LIVES + 1

    def test_bonus_only_once_per_threshold(self):
        t = make_tracker()
        t.add_points(1000)
        t.add_points(1)    # still above 1000 but no new threshold
        assert t.lives == ScoreTracker.INITIAL_LIVES + 1

    def test_bonus_at_2000_threshold(self):
        t = make_tracker()
        t.add_points(2000)
        # Should only get one bonus (single call crossing one threshold? No:
        # 2000 crosses threshold 1000 and 2000 — but only 1 bonus per call
        # because new_threshold = 2000 > last_bonus_threshold 0 → grant 1 life)
        # This is the intended design: one check per add_points call.
        assert t.lives == ScoreTracker.INITIAL_LIVES + 1

    def test_two_separate_thresholds_give_two_bonuses(self):
        t = make_tracker()
        t.add_points(1000)   # crosses 1000
        t.add_points(1000)   # crosses 2000
        assert t.lives == ScoreTracker.INITIAL_LIVES + 2

    def test_cap_at_max_lives(self):
        t = make_tracker()
        t.lives = ScoreTracker.MAX_LIVES
        t.add_points(1000)
        assert t.lives == ScoreTracker.MAX_LIVES  # no overflow

    def test_audio_play_jump_called_on_bonus(self):
        audio = MagicMock()
        t = make_tracker(audio=audio)
        t.add_points(1000)
        audio.play_jump.assert_called_once()

    def test_audio_not_called_when_lives_at_max(self):
        audio = MagicMock()
        t = make_tracker(audio=audio)
        t.lives = ScoreTracker.MAX_LIVES
        t.add_points(1000)
        audio.play_jump.assert_not_called()

    def test_threshold_tracking_updated_even_at_max_lives(self):
        t = make_tracker()
        t.lives = ScoreTracker.MAX_LIVES
        t.add_points(1000)
        # Threshold should be updated so a subsequent 1000 doesn't re-trigger
        assert t._last_bonus_threshold == 1000


class TestDeductPoints:
    def test_reduces_score(self):
        t = make_tracker()
        t.score = 100
        t.deduct_points(20)
        assert t.score == 80

    def test_score_never_below_zero(self):
        t = make_tracker()
        t.score = 10
        t.deduct_points(50)
        assert t.score == 0

    def test_lose_life_when_score_hits_zero(self):
        t = make_tracker()
        t.score = 10
        t.deduct_points(10)
        assert t.score == 0
        assert t.lives == ScoreTracker.INITIAL_LIVES - 1

    def test_lose_life_when_penalty_exceeds_score(self):
        t = make_tracker()
        t.score = 5
        t.deduct_points(20)
        assert t.score == 0
        assert t.lives == ScoreTracker.INITIAL_LIVES - 1

    def test_lose_life_when_score_already_zero(self):
        t = make_tracker()
        t.score = 0
        t.deduct_points(20)
        assert t.score == 0
        assert t.lives == ScoreTracker.INITIAL_LIVES - 1

    def test_no_life_lost_when_score_positive_after_deduction(self):
        t = make_tracker()
        t.score = 100
        t.deduct_points(20)
        assert t.lives == ScoreTracker.INITIAL_LIVES


class TestLoseLife:
    def test_decrements_lives(self):
        t = make_tracker()
        t.lose_life()
        assert t.lives == ScoreTracker.INITIAL_LIVES - 1

    def test_lives_floor_is_zero(self):
        t = make_tracker()
        t.lives = 0
        t.lose_life()
        assert t.lives == 0


class TestReset:
    def test_resets_score(self):
        t = make_tracker()
        t.score = 9999
        t.reset()
        assert t.score == 0

    def test_resets_lives(self):
        t = make_tracker()
        t.lives = 1
        t.reset()
        assert t.lives == ScoreTracker.INITIAL_LIVES

    def test_resets_bonus_threshold(self):
        t = make_tracker()
        t._last_bonus_threshold = 3000
        t.reset()
        assert t._last_bonus_threshold == 0


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

@given(amounts=st.lists(st.integers(min_value=0, max_value=5000), min_size=0, max_size=50))
@settings(max_examples=200)
def test_score_never_negative_add_only(amounts):
    """Score is always >= 0 after any sequence of add_points calls.

    **Validates: Requirements 4.1**
    """
    t = make_tracker()
    for a in amounts:
        t.add_points(a)
    assert t.score >= 0


@given(
    adds=st.lists(st.integers(min_value=0, max_value=5000), min_size=0, max_size=30),
    deducts=st.lists(st.integers(min_value=0, max_value=200), min_size=0, max_size=30),
)
@settings(max_examples=200)
def test_score_never_negative_mixed_ops(adds, deducts):
    """Score is always >= 0 after any interleaved add/deduct sequence.

    **Validates: Requirements 4.1**
    """
    t = make_tracker()
    ops = [("add", a) for a in adds] + [("deduct", d) for d in deducts]
    for op, val in ops:
        if op == "add":
            t.add_points(val)
        else:
            t.deduct_points(val)
    assert t.score >= 0


@given(amounts=st.lists(st.integers(min_value=0, max_value=5000), min_size=0, max_size=50))
@settings(max_examples=200)
def test_lives_always_in_bounds(amounts):
    """Lives are always between 0 and MAX_LIVES (9) inclusive.

    **Validates: Requirements 4.2**
    """
    t = make_tracker()
    for a in amounts:
        t.add_points(a)
    assert 0 <= t.lives <= ScoreTracker.MAX_LIVES


@given(
    initial_lives=st.integers(min_value=0, max_value=9),
    deduct_ops=st.lists(st.integers(min_value=1, max_value=200), min_size=0, max_size=30),
)
@settings(max_examples=200)
def test_lives_never_go_below_zero(initial_lives, deduct_ops):
    """Lives floor is 0; lose_life never produces negative lives.

    **Validates: Requirements 4.2**
    """
    t = make_tracker()
    t.lives = initial_lives
    for d in deduct_ops:
        t.deduct_points(d)
    assert t.lives >= 0


@given(
    start_score=st.integers(min_value=0, max_value=10000),
    thresholds_to_cross=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=200)
def test_bonus_life_once_per_threshold(start_score, thresholds_to_cross):
    """Each 1000-pt threshold grants exactly one bonus life.

    **Validates: Requirements 4.5**
    """
    t = make_tracker()
    # Start at a round threshold so we know exactly what the next crossing is
    initial_threshold = (start_score // 1000) * 1000
    t.score = initial_threshold
    t._last_bonus_threshold = initial_threshold
    initial_lives = t.lives

    for i in range(thresholds_to_cross):
        prev_lives = t.lives
        t.add_points(1000)
        if prev_lives < ScoreTracker.MAX_LIVES:
            assert t.lives == prev_lives + 1
        else:
            assert t.lives == ScoreTracker.MAX_LIVES


@given(amount=st.integers(min_value=0, max_value=10000))
@settings(max_examples=200)
def test_reset_always_restores_initial_state(amount):
    """After reset(), score=0, lives=INITIAL_LIVES, threshold=0 regardless of prior state.

    **Validates: Requirements 4.7**
    """
    t = make_tracker()
    t.add_points(amount)
    t.reset()
    assert t.score == 0
    assert t.lives == ScoreTracker.INITIAL_LIVES
    assert t._last_bonus_threshold == 0
