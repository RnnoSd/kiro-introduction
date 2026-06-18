"""Renderer — draws the current game state to a pygame.Surface.

Responsibilities:
- IDLE state: dark background + title + "Presiona ENTER para empezar"
- PLAYING state: Z-ordered render — background → bars → objects → projectiles → player → HUD
- GAME_OVER state: dark overlay + "GAME OVER" + final score + restart/exit options

Requirements: 10.2, 10.3, 10.4, 10.5
"""
import pygame

from src.state import State
from src.state_manager import StateManager


class Renderer:
    """Stateless renderer that draws the full frame for any game state."""

    # Colour constants
    _COLOR_IDLE_BG = (20, 20, 60)          # dark blue
    _COLOR_GAME_OVER_BG = (40, 0, 0)       # very dark red
    _COLOR_WHITE = (255, 255, 255)
    _COLOR_YELLOW = (255, 220, 50)
    _COLOR_RED = (220, 60, 60)
    _COLOR_LIGHT_GREY = (200, 200, 200)

    def render(self, surface: pygame.Surface, state_manager: StateManager) -> None:
        """Render the current game state to *surface*.

        Args:
            surface:       The pygame display surface to draw on.
            state_manager: The StateManager that owns all subsystems and current state.
        """
        state = state_manager.get_state()

        if state == State.IDLE:
            self._render_idle(surface, state_manager)
        elif state == State.PLAYING:
            self._render_playing(surface, state_manager)
        elif state == State.GAME_OVER:
            self._render_game_over(surface, state_manager)

    # ------------------------------------------------------------------
    # Per-state render methods
    # ------------------------------------------------------------------

    def _render_idle(self, surface: pygame.Surface, state_manager: StateManager) -> None:
        """IDLE screen: title + 'Presiona ENTER para empezar'.

        Requirement 10 (intro): show the idle/start screen before gameplay begins.
        """
        # Fill dark background
        surface.fill(self._COLOR_IDLE_BG)

        # Optionally draw the scrolling background (if available) for visual polish
        try:
            state_manager._background.render(surface)
        except Exception:
            pass

        width = surface.get_width()
        height = surface.get_height()

        # Title
        title_font = pygame.font.Font(None, 72)
        title_surf = title_font.render("Flappy Kiro", True, self._COLOR_YELLOW)
        title_rect = title_surf.get_rect(center=(width // 2, height // 2 - 70))
        surface.blit(title_surf, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 40)
        subtitle_surf = subtitle_font.render(
            "Presiona ENTER para empezar", True, self._COLOR_WHITE
        )
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 2 + 10))
        surface.blit(subtitle_surf, subtitle_rect)

    def _render_playing(self, surface: pygame.Surface, state_manager: StateManager) -> None:
        """PLAYING screen: Z-ordered render of all game objects.

        Z order: background → bars → objects → projectiles → player → HUD.
        Requirement 10.1 (active gameplay rendering).
        """
        state_manager._background.render(surface)
        state_manager._bar_manager.render(surface)
        state_manager._object_manager.render(surface)
        state_manager._projectile_manager.render(surface)
        state_manager._player.render(surface)
        state_manager._score_tracker.render(surface)

    def _render_game_over(self, surface: pygame.Surface, state_manager: StateManager) -> None:
        """GAME OVER screen: final score + restart/exit options.

        Requirements:
          10.2 — show final score obtained during the game.
          10.3 — show two selectable options: "Reiniciar" and "Salir".
          10.4 — ENTER triggers restart.
          10.5 — ESC triggers exit.
        """
        width = surface.get_width()
        height = surface.get_height()

        # Dark overlay background
        surface.fill(self._COLOR_GAME_OVER_BG)

        # "GAME OVER" heading
        heading_font = pygame.font.Font(None, 80)
        heading_surf = heading_font.render("GAME OVER", True, self._COLOR_RED)
        heading_rect = heading_surf.get_rect(center=(width // 2, height // 2 - 100))
        surface.blit(heading_surf, heading_rect)

        # Final score  (Requirement 10.2)
        score = state_manager._score_tracker.score
        score_font = pygame.font.Font(None, 48)
        score_surf = score_font.render(
            f"Puntuación final: {score}", True, self._COLOR_WHITE
        )
        score_rect = score_surf.get_rect(center=(width // 2, height // 2))
        surface.blit(score_surf, score_rect)

        # Selectable options  (Requirement 10.3, 10.4, 10.5)
        option_font = pygame.font.Font(None, 36)

        restart_surf = option_font.render("ENTER  —  Reiniciar", True, self._COLOR_LIGHT_GREY)
        restart_rect = restart_surf.get_rect(center=(width // 2, height // 2 + 70))
        surface.blit(restart_surf, restart_rect)

        quit_surf = option_font.render("ESC  —  Salir", True, self._COLOR_LIGHT_GREY)
        quit_rect = quit_surf.get_rect(center=(width // 2, height // 2 + 115))
        surface.blit(quit_surf, quit_rect)
