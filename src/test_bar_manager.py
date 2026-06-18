"""Unit tests for BarManager and BarPair (Requirements 3.1, 3.2, 3.5, 3.6)."""
import pytest
from src.bar_manager import BarPair, BarManager
from src.config import BarsConfig, CanvasConfig


# ---------------------------------------------------------------------------
# BarPair property tests
# ---------------------------------------------------------------------------

def make_pair(x=100.0, gap_y=300.0, gap_size=175.0, bar_width=60.0) -> BarPair:
    return BarPair(x=x, gap_y=gap_y, gap_size=gap_size, bar_width=bar_width)


def test_bounds_top_correct_geometry():
    pair = make_pair(x=50.0, gap_y=300.0, gap_size=150.0)
    top = pair.bounds_top
    # Top bar should start at y=0 and reach up to gap_y - gap_size/2 = 225
    assert top.x == 50.0
    assert top.y == 0.0
    assert top.height == pytest.approx(225.0)
    assert top.width == 60.0


def test_bounds_bottom_correct_geometry():
    pair = make_pair(x=50.0, gap_y=300.0, gap_size=150.0)
    bottom = pair.bounds_bottom
    # Bottom bar should start at gap_y + gap_size/2 = 375
    assert bottom.x == 50.0
    assert bottom.y == pytest.approx(375.0)
    assert bottom.width == 60.0


def test_bounds_top_zero_height_when_gap_at_top():
    """When gap center is very close to the top, top bar height clamps to 0."""
    pair = make_pair(gap_y=50.0, gap_size=200.0)
    # gap_y - gap_size/2 = 50 - 100 = -50  → should clamp to 0
    assert pair.bounds_top.height == 0.0


def test_bar_pair_defaults_not_scored():
    pair = make_pair()
    assert pair.scored is False


# ---------------------------------------------------------------------------
# BarManager initialisation
# ---------------------------------------------------------------------------

def make_manager() -> BarManager:
    return BarManager(BarsConfig(), CanvasConfig())


def test_initial_spawn_on_construction():
    bm = make_manager()
    assert len(bm.active_bars) == 1
    bar = bm.active_bars[0]
    assert bar.x == pytest.approx(800.0)  # canvas width


def test_initial_bar_gap_y_within_bounds():
    cfg = BarsConfig()
    for _ in range(50):
        bm = make_manager()
        bar = bm.active_bars[0]
        assert cfg.min_gap_y <= bar.gap_y <= cfg.max_gap_y


def test_initial_bar_gap_size_within_bounds():
    cfg = BarsConfig()
    for _ in range(50):
        bm = make_manager()
        bar = bm.active_bars[0]
        assert cfg.gap_size_min <= bar.gap_size <= cfg.gap_size_max


# ---------------------------------------------------------------------------
# update(): scrolling
# ---------------------------------------------------------------------------

def test_update_moves_bar_left():
    bm = make_manager()
    initial_x = bm.active_bars[0].x
    bm.update(1.0)
    assert bm.active_bars[0].x == pytest.approx(initial_x - BarsConfig().scroll_speed)


def test_update_zero_delta_does_not_move():
    bm = make_manager()
    initial_x = bm.active_bars[0].x
    bm.update(0.0)
    assert bm.active_bars[0].x == pytest.approx(initial_x)


# ---------------------------------------------------------------------------
# update(): spawning
# ---------------------------------------------------------------------------

def test_new_bar_spawned_when_rightmost_far_from_right_edge():
    """After the initial bar scrolls far enough left, a second bar should appear."""
    bm = make_manager()
    cfg = BarsConfig()
    canvas = CanvasConfig()
    # The rightmost bar starts at x=800 (right at right edge, so distance=0).
    # Scroll it left by enough so distance_to_right >= spawn_distance (200).
    # distance = canvas.width - (bar.x + bar_width) = 800 - (800-displacement+60)
    # We need: 800 - (800 - displacement + 60) >= 200
    #          displacement - 60 >= 200  →  displacement >= 260
    bm.update(260.0 / cfg.scroll_speed)
    assert len(bm.active_bars) >= 2


def test_no_extra_spawn_when_rightmost_close_to_right_edge():
    """A tiny update should not trigger a second spawn."""
    bm = make_manager()
    bm.update(0.01)
    assert len(bm.active_bars) == 1


# ---------------------------------------------------------------------------
# update(): off-screen removal
# ---------------------------------------------------------------------------

def test_bar_removed_when_off_screen():
    """A bar that scrolls completely to the left of x=0 is removed."""
    bm = make_manager()
    cfg = BarsConfig()
    # Move bars so far left that bar.x + width <= 0
    # bar starts at 800, width=60; need to move 860 px
    bm.update(860.0 / cfg.scroll_speed)
    # After removal, a new bar must have been spawned (manager never stays empty)
    # but the original bar should be gone.
    assert all(b.x + cfg.width > 0 for b in bm.active_bars)


def test_manager_never_empty_after_all_bars_leave():
    """When all bars leave the screen the manager immediately spawns a replacement."""
    bm = make_manager()
    cfg = BarsConfig()
    bm.update(1000.0 / cfg.scroll_speed)
    assert len(bm.active_bars) >= 1


# ---------------------------------------------------------------------------
# update(): scoring
# ---------------------------------------------------------------------------

def test_scored_flag_set_when_player_passes_bar():
    bm = make_manager()
    bar = bm.active_bars[0]
    cfg = BarsConfig()
    # player_left_x just beyond bar right edge
    player_x = bar.x + cfg.width + 1.0
    bm.update(0.0, player_left_x=player_x)
    assert bar.scored is True


def test_scored_flag_not_set_when_player_before_bar():
    bm = make_manager()
    bar = bm.active_bars[0]
    cfg = BarsConfig()
    player_x = bar.x - 10.0  # behind bar
    bm.update(0.0, player_left_x=player_x)
    assert bar.scored is False


def test_scored_flag_not_set_twice():
    """Once scored, additional updates don't re-trigger scoring."""
    bm = make_manager()
    bar = bm.active_bars[0]
    cfg = BarsConfig()
    player_x = bar.x + cfg.width + 1.0
    bm.update(0.0, player_left_x=player_x)
    assert bar.scored is True
    bar.scored = True  # already True
    bm.update(0.0, player_left_x=player_x)
    assert bar.scored is True  # still True, not toggled


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_and_spawns_fresh_bar():
    bm = make_manager()
    # Let multiple bars accumulate
    bm.update(0.5)  # may or may not spawn a second bar, but original remains
    bm.reset()
    assert len(bm.active_bars) == 1
    bar = bm.active_bars[0]
    assert bar.x == pytest.approx(800.0)
    assert bar.scored is False
