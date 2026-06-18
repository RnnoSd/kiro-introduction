"""Unit tests for Player class (task 5.1).

Tests cover:
- Base and boost speed movement
- Diagonal movement (independent X and Y axes)
- Canvas boundary clamping
- Brake state: no movement while braking, timer expiry clears brake
- Timer decrement: brake_timer, cooldown_*, invulnerable_timer
- reset() restores position and clears all cooldowns
"""

import pytest
from src.player import Player
from src.models import Vector2
from src.config import PlayerConfig, CanvasConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_player(x: float = 150.0, y: float = 300.0) -> Player:
    """Create a Player with default config at the given position."""
    return Player(
        position=Vector2(x=x, y=y),
        config=PlayerConfig(),
        canvas=CanvasConfig(),
    )


DELTA = 1.0  # 1 second delta_time for easy arithmetic


# ---------------------------------------------------------------------------
# Movement: base speed
# ---------------------------------------------------------------------------

class TestBaseMovement:
    def test_move_right_base_speed(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (1, 0), boost_active=False)
        assert p.position.x == pytest.approx(200.0 + 5.0)
        assert p.position.y == pytest.approx(300.0)

    def test_move_left_base_speed(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (-1, 0), boost_active=False)
        assert p.position.x == pytest.approx(200.0 - 5.0)

    def test_move_down_base_speed(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (0, 1), boost_active=False)
        assert p.position.y == pytest.approx(300.0 + 5.0)

    def test_move_up_base_speed(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (0, -1), boost_active=False)
        assert p.position.y == pytest.approx(300.0 - 5.0)

    def test_no_movement_on_zero_vector(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (0, 0), boost_active=False)
        assert p.position.x == pytest.approx(200.0)
        assert p.position.y == pytest.approx(300.0)


# ---------------------------------------------------------------------------
# Movement: boost speed
# ---------------------------------------------------------------------------

class TestBoostMovement:
    def test_boost_right(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (1, 0), boost_active=True)
        assert p.position.x == pytest.approx(200.0 + 10.0)

    def test_boost_up(self):
        p = make_player(x=200.0, y=300.0)
        p.update(DELTA, (0, -1), boost_active=True)
        assert p.position.y == pytest.approx(300.0 - 10.0)


# ---------------------------------------------------------------------------
# Diagonal movement: X and Y applied independently
# ---------------------------------------------------------------------------

class TestDiagonalMovement:
    def test_diagonal_down_right(self):
        p = make_player(x=200.0, y=200.0)
        p.update(DELTA, (1, 1), boost_active=False)
        assert p.position.x == pytest.approx(200.0 + 5.0)
        assert p.position.y == pytest.approx(200.0 + 5.0)

    def test_diagonal_up_left(self):
        p = make_player(x=200.0, y=200.0)
        p.update(DELTA, (-1, -1), boost_active=False)
        assert p.position.x == pytest.approx(200.0 - 5.0)
        assert p.position.y == pytest.approx(200.0 - 5.0)

    def test_diagonal_boost(self):
        p = make_player(x=200.0, y=200.0)
        p.update(DELTA, (1, -1), boost_active=True)
        assert p.position.x == pytest.approx(200.0 + 10.0)
        assert p.position.y == pytest.approx(200.0 - 10.0)


# ---------------------------------------------------------------------------
# Canvas boundary clamping
# ---------------------------------------------------------------------------

class TestClamping:
    def test_clamp_left_edge(self):
        p = make_player(x=2.0, y=300.0)
        p.update(DELTA, (-1, 0), boost_active=False)  # would go to -3
        assert p.position.x == pytest.approx(0.0)

    def test_clamp_right_edge(self):
        canvas = CanvasConfig()
        config = PlayerConfig()
        # Place player near right edge
        p = make_player(x=float(canvas.width - config.sprite_width - 2), y=300.0)
        p.update(DELTA, (1, 0), boost_active=False)  # would overshoot
        assert p.position.x == pytest.approx(canvas.width - config.sprite_width)

    def test_clamp_top_edge(self):
        p = make_player(x=200.0, y=2.0)
        p.update(DELTA, (0, -1), boost_active=False)  # would go to -3
        assert p.position.y == pytest.approx(0.0)

    def test_clamp_bottom_edge(self):
        canvas = CanvasConfig()
        config = PlayerConfig()
        p = make_player(x=200.0, y=float(canvas.height - config.sprite_height - 2))
        p.update(DELTA, (0, 1), boost_active=False)  # would overshoot
        assert p.position.y == pytest.approx(canvas.height - config.sprite_height)

    def test_already_at_origin_no_negative(self):
        p = make_player(x=0.0, y=0.0)
        p.update(DELTA, (-1, -1), boost_active=True)
        assert p.position.x == pytest.approx(0.0)
        assert p.position.y == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Brake state
# ---------------------------------------------------------------------------

class TestBrakeState:
    def test_braking_prevents_movement(self):
        p = make_player(x=200.0, y=300.0)
        p.is_braking = True
        p.brake_timer = 2.0
        p.update(DELTA, (1, 1), boost_active=True)
        assert p.position.x == pytest.approx(200.0)
        assert p.position.y == pytest.approx(300.0)

    def test_brake_timer_expires_clears_braking(self):
        p = make_player(x=200.0, y=300.0)
        p.is_braking = True
        p.brake_timer = 0.5
        # After 1s delta_time the timer hits 0 and braking clears
        p.update(DELTA, (1, 0), boost_active=False)
        assert p.is_braking is False

    def test_brake_timer_still_active_stays_braking(self):
        p = make_player(x=200.0, y=300.0)
        p.is_braking = True
        p.brake_timer = 2.0
        p.update(0.5, (1, 0), boost_active=False)
        assert p.is_braking is True
        assert p.brake_timer == pytest.approx(1.5)

    def test_movement_resumes_after_brake_expires(self):
        p = make_player(x=200.0, y=300.0)
        p.is_braking = True
        p.brake_timer = 0.5
        p.update(1.0, (1, 0), boost_active=False)
        # Once brake_timer reaches 0, is_braking is cleared and movement is applied this frame
        assert p.is_braking is False
        assert p.position.x == pytest.approx(200.0 + 5.0)


# ---------------------------------------------------------------------------
# Timer decrement
# ---------------------------------------------------------------------------

class TestTimerDecrement:
    def test_cooldown_shoot_decrements(self):
        p = make_player()
        p.cooldown_shoot = 0.5
        p.update(0.3, (0, 0), boost_active=False)
        assert p.cooldown_shoot == pytest.approx(0.2)

    def test_cooldown_dash_decrements(self):
        p = make_player()
        p.cooldown_dash = 1.0
        p.update(0.4, (0, 0), boost_active=False)
        assert p.cooldown_dash == pytest.approx(0.6)

    def test_cooldown_brake_decrements(self):
        p = make_player()
        p.cooldown_brake = 5.0
        p.update(1.0, (0, 0), boost_active=False)
        assert p.cooldown_brake == pytest.approx(4.0)

    def test_invulnerable_timer_decrements(self):
        p = make_player()
        p.invulnerable_timer = 1.0
        p.update(0.25, (0, 0), boost_active=False)
        assert p.invulnerable_timer == pytest.approx(0.75)

    def test_timers_do_not_go_below_zero(self):
        p = make_player()
        p.cooldown_shoot = 0.1
        p.cooldown_dash = 0.1
        p.cooldown_brake = 0.1
        p.invulnerable_timer = 0.1
        p.brake_timer = 0.1
        p.update(10.0, (0, 0), boost_active=False)
        assert p.cooldown_shoot == pytest.approx(0.0)
        assert p.cooldown_dash == pytest.approx(0.0)
        assert p.cooldown_brake == pytest.approx(0.0)
        assert p.invulnerable_timer == pytest.approx(0.0)
        assert p.brake_timer == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# bounds property
# ---------------------------------------------------------------------------

class TestBounds:
    def test_bounds_matches_position_and_config(self):
        p = make_player(x=100.0, y=200.0)
        b = p.bounds
        assert b.x == pytest.approx(100.0)
        assert b.y == pytest.approx(200.0)
        assert b.width == p.config.sprite_width
        assert b.height == p.config.sprite_height

    def test_bounds_updates_after_move(self):
        p = make_player(x=100.0, y=200.0)
        p.update(DELTA, (1, 0), boost_active=False)
        assert p.bounds.x == pytest.approx(100.0 + 5.0)


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_restores_position(self):
        p = make_player(x=400.0, y=400.0)
        p.update(DELTA, (1, 1), boost_active=False)
        p.reset()
        assert p.position.x == pytest.approx(p.config.start_x)
        assert p.position.y == pytest.approx(p.config.start_y)

    def test_reset_clears_all_timers(self):
        p = make_player()
        p.brake_timer = 3.0
        p.cooldown_shoot = 0.5
        p.cooldown_dash = 1.0
        p.cooldown_brake = 5.0
        p.invulnerable_timer = 1.0
        p.is_braking = True
        p.reset()
        assert p.brake_timer == pytest.approx(0.0)
        assert p.cooldown_shoot == pytest.approx(0.0)
        assert p.cooldown_dash == pytest.approx(0.0)
        assert p.cooldown_brake == pytest.approx(0.0)
        assert p.invulnerable_timer == pytest.approx(0.0)
        assert p.is_braking is False


# ---------------------------------------------------------------------------
# try_shoot()  (task 5.2)
# ---------------------------------------------------------------------------

from src.player import Projectile  # noqa: E402 — import after Player tests block


class TestTryShoot:
    def test_returns_projectile_when_cooldown_zero(self):
        p = make_player(x=150.0, y=300.0)
        assert p.cooldown_shoot == 0.0
        result = p.try_shoot()
        assert result is not None
        assert isinstance(result, Projectile)

    def test_returns_none_when_cooldown_active(self):
        p = make_player()
        p.cooldown_shoot = 0.3
        result = p.try_shoot()
        assert result is None

    def test_activates_cooldown_after_shoot(self):
        p = make_player()
        p.try_shoot()
        assert p.cooldown_shoot == pytest.approx(p.config.cooldown_shoot)

    def test_projectile_spawns_at_right_edge(self):
        p = make_player(x=150.0, y=300.0)
        result = p.try_shoot()
        expected_x = 150.0 + p.config.sprite_width
        assert result.position.x == pytest.approx(expected_x)

    def test_projectile_y_is_vertically_centered(self):
        p = make_player(x=150.0, y=300.0)
        result = p.try_shoot()
        expected_y = 300.0 + (p.config.sprite_height // 2) - 3
        assert result.position.y == pytest.approx(expected_y)

    def test_projectile_bounds_dimensions(self):
        p = make_player()
        result = p.try_shoot()
        assert result.bounds.width == pytest.approx(20.0)
        assert result.bounds.height == pytest.approx(6.0)

    def test_second_shoot_blocked_by_cooldown(self):
        p = make_player()
        first = p.try_shoot()
        assert first is not None
        second = p.try_shoot()
        assert second is None

    def test_shoot_allowed_again_after_cooldown_expires(self):
        p = make_player()
        p.try_shoot()
        # Drain the cooldown via update
        p.update(p.config.cooldown_shoot + 0.01, (0, 0), boost_active=False)
        result = p.try_shoot()
        assert result is not None


# ---------------------------------------------------------------------------
# try_dash_back()  (task 5.2)
# ---------------------------------------------------------------------------

class TestTryDashBack:
    def test_moves_x_back_100px(self):
        p = make_player(x=300.0, y=300.0)
        p.try_dash_back()
        assert p.position.x == pytest.approx(200.0)

    def test_clamps_to_zero(self):
        p = make_player(x=50.0, y=300.0)
        p.try_dash_back()
        assert p.position.x == pytest.approx(0.0)

    def test_activates_cooldown(self):
        p = make_player(x=300.0)
        p.try_dash_back()
        assert p.cooldown_dash == pytest.approx(p.config.cooldown_dash)

    def test_does_nothing_when_cooldown_active(self):
        p = make_player(x=300.0)
        p.cooldown_dash = 0.5
        p.try_dash_back()
        assert p.position.x == pytest.approx(300.0)
        assert p.cooldown_dash == pytest.approx(0.5)  # unchanged

    def test_second_dash_blocked_by_cooldown(self):
        p = make_player(x=500.0)
        p.try_dash_back()
        x_after_first = p.position.x
        p.try_dash_back()
        assert p.position.x == pytest.approx(x_after_first)  # no second dash

    def test_dash_allowed_again_after_cooldown_expires(self):
        p = make_player(x=500.0)
        p.try_dash_back()
        x_after_first = p.position.x
        p.update(p.config.cooldown_dash + 0.01, (0, 0), boost_active=False)
        p.try_dash_back()
        assert p.position.x == pytest.approx(max(0.0, x_after_first - 100.0))


# ---------------------------------------------------------------------------
# try_brake()  (task 5.2)
# ---------------------------------------------------------------------------

class TestTryBrake:
    def test_activates_braking(self):
        p = make_player()
        p.try_brake()
        assert p.is_braking is True

    def test_sets_brake_timer(self):
        p = make_player()
        p.try_brake()
        assert p.brake_timer == pytest.approx(p.config.brake_duration)

    def test_sets_brake_cooldown(self):
        p = make_player()
        p.try_brake()
        assert p.cooldown_brake == pytest.approx(p.config.cooldown_brake)

    def test_does_nothing_when_cooldown_active(self):
        p = make_player()
        p.cooldown_brake = 3.0
        p.try_brake()
        assert p.is_braking is False
        assert p.brake_timer == pytest.approx(0.0)

    def test_second_brake_blocked_by_cooldown(self):
        p = make_player()
        p.try_brake()
        brake_timer_after_first = p.brake_timer
        # Manually drain brake_timer (not the cooldown) to simulate brake expiry mid-cooldown
        p.brake_timer = 0.0
        p.is_braking = False
        p.try_brake()
        # cooldown_brake is still active, so no new brake
        assert p.is_braking is False
        assert p.brake_timer == pytest.approx(0.0)

    def test_brake_allowed_again_after_cooldown_expires(self):
        p = make_player()
        p.try_brake()
        p.update(p.config.cooldown_brake + 0.01, (0, 0), boost_active=False)
        # After full cooldown, is_braking was cleared by update; try again
        p.try_brake()
        assert p.is_braking is True
        assert p.brake_timer == pytest.approx(p.config.brake_duration)
