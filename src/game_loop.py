"""GameLoop — drives the game at 60 fps using pygame.time.Clock.

Responsibilities:
- Initialize pygame and create the display window
- Run the main loop with delta-time capped to 0.1 s
- Forward pygame events to InputHandler and dispatch resulting actions
- Call state_manager.tick(delta_time) every frame
- Handle pygame.QUIT cleanly via stop()
- Call renderer.render(surface, state_manager) every frame when a renderer is provided

Requirements: 1, 2, 6, 7, 8, 10
"""
import pygame

from src.config import GameConfig
from src.state import State
from src.state_manager import StateManager
from src.input_handler import InputHandler


class GameLoop:
    """Main game loop controller.

    Args:
        config:        GameConfig with canvas dimensions and all sub-configs.
        state_manager: StateManager that owns game state and orchestrates subsystems.
        input_handler: InputHandler that translates pygame events to game actions.
        renderer:      Optional renderer; called as renderer.render(surface, state_manager)
                       each frame.
    """

    def __init__(
        self,
        config: GameConfig,
        state_manager: StateManager,
        input_handler: InputHandler,
        renderer=None,
    ):
        self._config = config
        self._state_manager = state_manager
        self._input_handler = input_handler
        self._renderer = renderer
        self._running: bool = False
        self._surface: pygame.Surface | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialize pygame, open the window, and run the main loop until stop() is called."""
        # pygame.init() and display.set_mode() may have already been called in main.py
        # (required before asset loading so convert_alpha() works). Reuse the existing
        # surface if it's already set up; create it only when needed.
        if not pygame.get_init():
            pygame.init()
        existing = pygame.display.get_surface()
        if existing is not None:
            self._surface = existing
        else:
            self._surface = pygame.display.set_mode(
                (self._config.canvas.width, self._config.canvas.height)
            )
            pygame.display.set_caption("Flappy Kiro")

        clock = pygame.time.Clock()
        self._running = True

        while self._running:
            # --- Delta time: ms → seconds, capped to 0.1 s to prevent physics explosions ---
            raw_ms = clock.tick(60)
            delta_time: float = min(raw_ms / 1000.0, 0.1)

            # --- Event processing ---
            events = pygame.event.get()
            actions = self._input_handler.process_events(events)

            # Guard: handle pygame.QUIT directly as well (InputHandler also does this,
            # but we stop immediately to avoid an extra loop iteration).
            for event in events:
                if event.type == pygame.QUIT:
                    self.stop()
                    return

            # --- Dispatch discrete one-shot actions ---
            should_stop = self._dispatch_actions(actions)
            if should_stop:
                return

            # --- Per-frame game tick (player movement + all subsystems) ---
            self.on_tick(delta_time)

            # --- Rendering ---
            if self._renderer is not None and self._surface is not None:
                self._renderer.render(self._surface, self._state_manager)
                pygame.display.flip()

    def stop(self) -> None:
        """Signal the loop to stop and shut down pygame."""
        self._running = False
        pygame.quit()

    def on_tick(self, delta_time: float) -> None:
        """Called once per frame with the capped delta time in seconds.

        Passes the current movement vector and boost state from InputHandler to
        StateManager.tick() so the player position is updated before collision
        detection runs.

        Extracted as a separate method for testability — tests can drive individual
        frames without running the full pygame event pump.
        """
        movement_vector = self._input_handler.get_movement_vector()
        boost_active = self._input_handler.is_boost_active()
        self._state_manager.tick(delta_time, movement_vector, boost_active)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch_actions(self, actions: list) -> bool:
        """Route input actions to the appropriate subsystem based on current state.

        Returns True if the loop should stop (quit action received).

        IDLE state:
          'restart' (ENTER) → state_manager.on_restart()

        PLAYING state:
          'shoot'  → player.try_shoot(); if projectile returned, pass to projectile_manager.spawn()
          'dash'   → player.try_dash_back()
          'brake'  → player.try_brake()

        GAME_OVER state:
          'restart' → state_manager.on_restart()
          'quit'    → state_manager.on_quit()

        'quit' in any state (ESC / window close) → stop() and return True
        """
        current_state = self._state_manager.get_state()
        player = self._state_manager._player
        projectile_manager = self._state_manager._projectile_manager

        for action in actions:
            if action == 'quit':
                self.stop()
                return True

            if current_state == State.IDLE:
                if action == 'restart':
                    self._state_manager.on_restart()

            elif current_state == State.PLAYING:
                if action == 'shoot':
                    projectile = player.try_shoot()
                    if projectile is not None:
                        # Spawn at the projectile's computed origin position
                        projectile_manager.spawn(projectile.position)
                        # Play shoot sound
                        self._state_manager.play_shoot_sound()
                elif action == 'dash':
                    player.try_dash_back()
                elif action == 'brake':
                    player.try_brake()

            elif current_state == State.GAME_OVER:
                if action == 'restart':
                    self._state_manager.on_restart()
                elif action == 'quit':
                    self._state_manager.on_quit()

        return False
