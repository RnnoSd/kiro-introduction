"""Tests for AudioService (Requirements 9.1–9.5)."""
import pytest
from unittest.mock import MagicMock
from src.audio_service import AudioService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cache(jump=None, penalty=None):
    """Build a minimal AssetCache stub with the given sound objects."""
    cache = MagicMock()
    cache.audio = {"jump": jump, "penalty": penalty}
    return cache


def _ok_sound():
    """Return a mock that behaves as a working pygame.mixer.Sound."""
    sound = MagicMock()
    sound.play.return_value = None
    return sound


def _bad_sound():
    """Return a mock whose play() raises an exception (mixer unavailable)."""
    sound = MagicMock()
    sound.play.side_effect = Exception("mixer not available")
    return sound


# ---------------------------------------------------------------------------
# Requirement 9.1 — AudioService initialises from asset cache
# ---------------------------------------------------------------------------

class TestInit:
    def test_both_sounds_loaded(self):
        jump = _ok_sound()
        penalty = _ok_sound()
        svc = AudioService(_make_cache(jump=jump, penalty=penalty))
        assert svc._jump_sound is jump
        assert svc._penalty_sound is penalty

    def test_both_sounds_none(self):
        svc = AudioService(_make_cache())
        assert svc._jump_sound is None
        assert svc._penalty_sound is None

    def test_missing_key_treated_as_none(self):
        # cache with no audio keys at all
        cache = MagicMock()
        cache.audio = {}
        svc = AudioService(cache)
        assert svc._jump_sound is None
        assert svc._penalty_sound is None


# ---------------------------------------------------------------------------
# Requirement 9.2 + 9.4 — play_jump
# ---------------------------------------------------------------------------

class TestPlayJump:
    def test_plays_when_sound_available(self):
        sound = _ok_sound()
        svc = AudioService(_make_cache(jump=sound))
        svc.play_jump()
        sound.play.assert_called_once()

    def test_silent_when_jump_is_none(self):
        """Req 9.4: if jump.wav was not loaded, play_jump does nothing."""
        svc = AudioService(_make_cache(jump=None))
        # Must not raise
        svc.play_jump()

    def test_disables_jump_after_play_exception(self):
        """Req 9.4: if play() raises, that sound is disabled permanently."""
        sound = _bad_sound()
        svc = AudioService(_make_cache(jump=sound))
        svc.play_jump()              # triggers exception → disables jump
        assert svc._jump_sound is None

    def test_subsequent_calls_silent_after_disable(self):
        sound = _bad_sound()
        svc = AudioService(_make_cache(jump=sound))
        svc.play_jump()   # disables
        svc.play_jump()   # must not raise a second time
        sound.play.assert_called_once()  # only attempted once

    def test_play_jump_does_not_raise(self):
        """play_jump must never propagate exceptions to the caller."""
        svc = AudioService(_make_cache(jump=_bad_sound()))
        try:
            svc.play_jump()
        except Exception as exc:
            pytest.fail(f"play_jump raised unexpectedly: {exc}")


# ---------------------------------------------------------------------------
# Requirement 9.3 + 9.5 — play_penalty
# ---------------------------------------------------------------------------

class TestPlayPenalty:
    def test_plays_when_sound_available(self):
        sound = _ok_sound()
        svc = AudioService(_make_cache(penalty=sound))
        svc.play_penalty()
        sound.play.assert_called_once()

    def test_silent_when_penalty_is_none(self):
        """Req 9.5: if game_over.wav was not loaded, play_penalty does nothing."""
        svc = AudioService(_make_cache(penalty=None))
        svc.play_penalty()  # must not raise

    def test_disables_penalty_after_play_exception(self):
        """Req 9.5: if play() raises, that sound is disabled permanently."""
        sound = _bad_sound()
        svc = AudioService(_make_cache(penalty=sound))
        svc.play_penalty()
        assert svc._penalty_sound is None

    def test_subsequent_calls_silent_after_disable(self):
        sound = _bad_sound()
        svc = AudioService(_make_cache(penalty=sound))
        svc.play_penalty()   # disables
        svc.play_penalty()   # must not raise
        sound.play.assert_called_once()

    def test_play_penalty_does_not_raise(self):
        """play_penalty must never propagate exceptions to the caller."""
        svc = AudioService(_make_cache(penalty=_bad_sound()))
        try:
            svc.play_penalty()
        except Exception as exc:
            pytest.fail(f"play_penalty raised unexpectedly: {exc}")


# ---------------------------------------------------------------------------
# Independence — Req 9.4/9.5: failure of one sound does not affect the other
# ---------------------------------------------------------------------------

class TestSoundIndependence:
    def test_jump_failure_does_not_affect_penalty(self):
        jump = _bad_sound()
        penalty = _ok_sound()
        svc = AudioService(_make_cache(jump=jump, penalty=penalty))

        svc.play_jump()       # jump fails → disabled
        svc.play_penalty()    # penalty must still work

        assert svc._jump_sound is None
        assert svc._penalty_sound is not None
        penalty.play.assert_called_once()

    def test_penalty_failure_does_not_affect_jump(self):
        jump = _ok_sound()
        penalty = _bad_sound()
        svc = AudioService(_make_cache(jump=jump, penalty=penalty))

        svc.play_penalty()    # penalty fails → disabled
        svc.play_jump()       # jump must still work

        assert svc._penalty_sound is None
        assert svc._jump_sound is not None
        jump.play.assert_called_once()

    def test_both_none_both_silent(self):
        svc = AudioService(_make_cache())
        svc.play_jump()
        svc.play_penalty()
        # both are no-ops; no exception raised
