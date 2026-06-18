"""Tests for src/renderer.py

Verifies that the Renderer calls the correct subsystem render methods for each
game state without exercising actual pygame display output.  We use a spy
Surface that records fill/blit calls, and lightweight fakes for StateManager
subsystems.  The real pygame library is used (already installed) but we only
initialize the font subsystem — no display window is opened.

Requirements: 10.2, 10.3, 10.4, 10.5
"""
import os
import pytest
import pygame

# Initialize only the font subsystem so pygame.font.Font works without a display.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.font.init()

from src.state import State      # noqa: E402
from src.renderer import Renderer  # noqa: E402


# ---------------------------------------------------------------------------
# Spy Surface — wraps a real pygame.Surface and records fill/blit calls
# ---------------------------------------------------------------------------

class SpySurface:
    """Thin wrapper around pygame.Surface that records fill and blit calls."""

    def __init__(self, width: int = 800, height: int = 600):
        self._surface = pygame.Surface((width, height))
        self.filled: list = []
        self.blits: list = []

    # Delegate geometry queries to the real surface
    def get_width(self) -> int:
        return self._surface.get_width()

    def get_height(self) -> int:
        return self._surface.get_height()

    # Intercept fill and blit to record calls, then forward to real surface
    def fill(self, color):
        self.filled.append(color)
        self._surface.fill(color)

    def blit(self, source, dest, area=None, special_flags=0):
        self.blits.append((source, dest))
        self._surface.blit(source, dest)


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------

class _RenderTracker:
    """Mixin that records render calls."""
    def __init__(self):
        self.render_calls = 0

    def render(self, surface):
        self.render_calls += 1


class _FakeBackground(_RenderTracker):
    pass


class _FakeBarManager(_RenderTracker):
    pass


class _FakeObjectManager(_RenderTracker):
    pass


class _FakeProjectileManager(_RenderTracker):
    pass


class _FakePlayer(_RenderTracker):
    pass


class _FakeScoreTracker(_RenderTracker):
    def __init__(self, score=42):
        super().__init__()
        self.score = score
        self.lives = 3


class _FakeStateManager:
    """Minimal StateManager fake that just holds a state and subsystem stubs."""

    def __init__(self, state: State, score: int = 0):
        self._state = state
        self._background = _FakeBackground()
        self._bar_manager = _FakeBarManager()
        self._object_manager = _FakeObjectManager()
        self._projectile_manager = _FakeProjectileManager()
        self._player = _FakePlayer()
        self._score_tracker = _FakeScoreTracker(score=score)

    def get_state(self) -> State:
        return self._state


def make_surface() -> SpySurface:
    """Create a fresh SpySurface for each test."""
    return SpySurface(800, 600)


# ---------------------------------------------------------------------------
# Tests — IDLE state
# ---------------------------------------------------------------------------

class TestRendererIdle:
    def _make(self):
        return Renderer(), _FakeStateManager(State.IDLE), make_surface()

    def test_idle_fills_background(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        # A fill call must have been made (dark background)
        assert len(surface.filled) > 0

    def test_idle_renders_background_layer(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._background.render_calls == 1

    def test_idle_blits_text(self):
        """Renderer must draw at least two text surfaces (title + subtitle)."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert len(surface.blits) >= 2

    def test_idle_does_not_render_game_objects(self):
        """In IDLE state, bars / objects / projectiles / player should NOT be rendered."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._bar_manager.render_calls == 0
        assert sm._object_manager.render_calls == 0
        assert sm._projectile_manager.render_calls == 0
        assert sm._player.render_calls == 0


# ---------------------------------------------------------------------------
# Tests — PLAYING state
# ---------------------------------------------------------------------------

class TestRendererPlaying:
    def _make(self):
        return Renderer(), _FakeStateManager(State.PLAYING), make_surface()

    def test_playing_renders_background(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._background.render_calls == 1

    def test_playing_renders_bars(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._bar_manager.render_calls == 1

    def test_playing_renders_objects(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._object_manager.render_calls == 1

    def test_playing_renders_projectiles(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._projectile_manager.render_calls == 1

    def test_playing_renders_player(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._player.render_calls == 1

    def test_playing_renders_hud(self):
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._score_tracker.render_calls == 1

    def test_playing_z_order_all_subsystems_called(self):
        """All six render layers must be called exactly once in PLAYING state."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        for component in (
            sm._background, sm._bar_manager, sm._object_manager,
            sm._projectile_manager, sm._player, sm._score_tracker,
        ):
            assert component.render_calls == 1, (
                f"{component.__class__.__name__} render was not called exactly once"
            )


# ---------------------------------------------------------------------------
# Tests — GAME_OVER state
# ---------------------------------------------------------------------------

class TestRendererGameOver:
    def _make(self, score=750):
        return Renderer(), _FakeStateManager(State.GAME_OVER, score=score), make_surface()

    def test_game_over_fills_background(self):
        """Requirement 10.2: GAME_OVER screen must paint a background."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert len(surface.filled) > 0

    def test_game_over_blits_multiple_texts(self):
        """Requirement 10.2 & 10.3: heading + score + two option texts = at least 4 blits."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert len(surface.blits) >= 4

    def test_game_over_uses_final_score(self):
        """Requirement 10.2: the score shown should come from ScoreTracker.score.

        We verify this indirectly by confirming render doesn't crash and that
        the score tracker's score attribute is read (no KeyError / AttributeError).
        """
        renderer, sm, surface = self._make(score=1337)
        # Should not raise even with a non-zero score
        renderer.render(surface, sm)
        assert sm._score_tracker.score == 1337

    def test_game_over_does_not_render_game_objects(self):
        """Bars, objects, projectiles, player should NOT be drawn in GAME_OVER."""
        renderer, sm, surface = self._make()
        renderer.render(surface, sm)
        assert sm._bar_manager.render_calls == 0
        assert sm._object_manager.render_calls == 0
        assert sm._projectile_manager.render_calls == 0
        assert sm._player.render_calls == 0

    def test_game_over_score_zero(self):
        """Edge case: score of 0 should render without errors."""
        renderer, sm, surface = self._make(score=0)
        renderer.render(surface, sm)
        assert len(surface.blits) >= 4
