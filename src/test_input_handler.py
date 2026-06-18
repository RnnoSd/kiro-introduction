"""Unit tests for InputHandler (src/input_handler.py).

pygame constants are used directly as integers — no display init needed.
Events are built as simple mock objects to avoid requiring a running pygame instance.
"""
import types
import pytest
import pygame

from src.input_handler import InputHandler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _keydown(key: int):
    """Create a minimal pygame KEYDOWN event-like object."""
    e = types.SimpleNamespace()
    e.type = pygame.KEYDOWN
    e.key = key
    return e


def _keyup(key: int):
    """Create a minimal pygame KEYUP event-like object."""
    e = types.SimpleNamespace()
    e.type = pygame.KEYUP
    e.key = key
    return e


def _quit_event():
    """Create a minimal pygame.QUIT event-like object."""
    e = types.SimpleNamespace()
    e.type = pygame.QUIT
    return e


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_keys_held_starts_empty(self):
        ih = InputHandler()
        assert ih.keys_held == set()

    def test_movement_vector_zero_by_default(self):
        ih = InputHandler()
        assert ih.get_movement_vector() == (0, 0)

    def test_boost_inactive_by_default(self):
        ih = InputHandler()
        assert ih.is_boost_active() is False


# ---------------------------------------------------------------------------
# process_events — discrete actions
# ---------------------------------------------------------------------------

class TestDiscreteActions:
    def test_a_key_returns_shoot(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_a)])
        assert 'shoot' in actions

    def test_w_key_returns_dash(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_w)])
        assert 'dash' in actions

    def test_s_key_returns_brake(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_s)])
        assert 'brake' in actions

    def test_enter_key_returns_restart(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_RETURN)])
        assert 'restart' in actions

    def test_escape_key_returns_quit(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_ESCAPE)])
        assert 'quit' in actions

    def test_quit_event_returns_quit(self):
        ih = InputHandler()
        actions = ih.process_events([_quit_event()])
        assert 'quit' in actions

    def test_arrow_key_does_not_produce_action(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_LEFT)])
        assert actions == []

    def test_space_key_does_not_produce_action(self):
        ih = InputHandler()
        actions = ih.process_events([_keydown(pygame.K_SPACE)])
        assert actions == []

    def test_multiple_actions_in_one_call(self):
        ih = InputHandler()
        actions = ih.process_events([
            _keydown(pygame.K_a),
            _keydown(pygame.K_w),
        ])
        assert 'shoot' in actions
        assert 'dash' in actions

    def test_empty_events_returns_empty_list(self):
        ih = InputHandler()
        assert ih.process_events([]) == []


# ---------------------------------------------------------------------------
# process_events — keys_held tracking
# ---------------------------------------------------------------------------

class TestKeysHeldTracking:
    def test_keydown_adds_to_keys_held(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_LEFT)])
        assert pygame.K_LEFT in ih.keys_held

    def test_keyup_removes_from_keys_held(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_LEFT)])
        ih.process_events([_keyup(pygame.K_LEFT)])
        assert pygame.K_LEFT not in ih.keys_held

    def test_keyup_unknown_key_is_safe(self):
        """KEYUP for a key never pressed must not raise."""
        ih = InputHandler()
        ih.process_events([_keyup(pygame.K_RIGHT)])  # was never held
        assert pygame.K_RIGHT not in ih.keys_held

    def test_multiple_keys_held_simultaneously(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_UP), _keydown(pygame.K_RIGHT)])
        assert pygame.K_UP in ih.keys_held
        assert pygame.K_RIGHT in ih.keys_held

    def test_action_key_also_tracked_in_keys_held(self):
        """Keys that fire discrete actions (e.g. A) must also be tracked in keys_held."""
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_a)])
        assert pygame.K_a in ih.keys_held


# ---------------------------------------------------------------------------
# get_movement_vector
# ---------------------------------------------------------------------------

class TestGetMovementVector:
    def test_left_arrow(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_LEFT)])
        assert ih.get_movement_vector() == (-1, 0)

    def test_right_arrow(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_RIGHT)])
        assert ih.get_movement_vector() == (1, 0)

    def test_up_arrow(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_UP)])
        assert ih.get_movement_vector() == (0, -1)

    def test_down_arrow(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_DOWN)])
        assert ih.get_movement_vector() == (0, 1)

    def test_diagonal_down_right(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_RIGHT), _keydown(pygame.K_DOWN)])
        assert ih.get_movement_vector() == (1, 1)

    def test_diagonal_up_left(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_LEFT), _keydown(pygame.K_UP)])
        assert ih.get_movement_vector() == (-1, -1)

    def test_opposite_horizontal_keys_cancel_out(self):
        """LEFT + RIGHT held simultaneously → dx = 0."""
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_LEFT), _keydown(pygame.K_RIGHT)])
        dx, _ = ih.get_movement_vector()
        assert dx == 0

    def test_opposite_vertical_keys_cancel_out(self):
        """UP + DOWN held simultaneously → dy = 0."""
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_UP), _keydown(pygame.K_DOWN)])
        _, dy = ih.get_movement_vector()
        assert dy == 0

    def test_no_keys_returns_zero_vector(self):
        ih = InputHandler()
        assert ih.get_movement_vector() == (0, 0)

    def test_vector_after_key_release(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_RIGHT)])
        ih.process_events([_keyup(pygame.K_RIGHT)])
        assert ih.get_movement_vector() == (0, 0)


# ---------------------------------------------------------------------------
# is_boost_active
# ---------------------------------------------------------------------------

class TestIsBoostActive:
    def test_space_held_activates_boost(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_SPACE)])
        assert ih.is_boost_active() is True

    def test_space_released_deactivates_boost(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_SPACE)])
        ih.process_events([_keyup(pygame.K_SPACE)])
        assert ih.is_boost_active() is False

    def test_other_key_does_not_activate_boost(self):
        ih = InputHandler()
        ih.process_events([_keydown(pygame.K_UP)])
        assert ih.is_boost_active() is False
