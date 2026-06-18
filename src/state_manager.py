"""StateManager — orchestrates all game subsystems and collision detection.

Requirements: 3.3, 3.4, 4.3, 4.4, 4.5, 4.6, 5.2, 5.3, 5.4, 5.6, 6.2, 10.1
"""
import sys
import pygame

from src.state import State
from src.models import rects_overlap
from src.config import GameConfig


class StateManager:
    """Owns the current game state and coordinates all subsystems per frame.

    Responsibilities:
    - Track state: IDLE, PLAYING, GAME_OVER
    - tick(delta_time): update all subsystems only in PLAYING state
    - Run collision detection: Kiro↔Bars, Kiro↔RedObjects, Kiro↔GreenObjects, Projectile↔RedObjects
    - Handle bar-passing score (+5 pts per pair)
    - Transition to GAME_OVER when lives reach 0
    - on_restart(): reset all subsystems and transition to PLAYING
    - on_quit(): close application cleanly
    """

    def __init__(
        self,
        config: GameConfig,
        background,
        player,
        bar_manager,
        object_manager,
        projectile_manager,
        score_tracker,
        audio_service=None,
    ):
        self._config = config
        self._background = background
        self._player = player
        self._bar_manager = bar_manager
        self._object_manager = object_manager
        self._projectile_manager = projectile_manager
        self._score_tracker = score_tracker
        self._audio_service = audio_service

        self._state: State = State.IDLE

    # ------------------------------------------------------------------
    # State accessors
    # ------------------------------------------------------------------

    def get_state(self) -> State:
        """Return the current game state."""
        return self._state

    def set_state(self, state: State) -> None:
        """Directly set the current game state."""
        self._state = state

    # ------------------------------------------------------------------
    # Per-frame orchestration
    # ------------------------------------------------------------------

    def tick(
        self,
        delta_time: float,
        movement_vector: tuple = (0, 0),
        boost_active: bool = False,
    ) -> None:
        """Update all subsystems and run collision detection.

        Only active while state is PLAYING. Background updates in any state
        since the design keeps it scrolling during play, but subsystem logic
        (physics, collisions, scoring) is guarded by PLAYING.

        Args:
            delta_time:      Time elapsed this frame in seconds (capped to 0.1 s).
            movement_vector: (dx, dy) from InputHandler.get_movement_vector().
            boost_active:    True when SPACE is held (from InputHandler.is_boost_active()).

        Requirements: 3.3, 3.4, 4.3, 4.4, 4.5, 4.6, 5.2, 5.3, 5.4, 5.6, 6.2, 10.1
        """
        if self._state != State.PLAYING:
            return

        # 1. Update player movement (timers + position)
        self._player.update(delta_time, movement_vector, boost_active)

        # 2. Update background scroll (always scrolls during play)
        self._background.update(delta_time)

        # 3. Update game objects
        self._bar_manager.update(delta_time, player_left_x=self._player.position.x)
        self._object_manager.update(delta_time)

        # 4. Projectile collisions with red objects — delegate to ProjectileManager
        red_objects = self._object_manager.get_red_objects()
        destroyed = self._projectile_manager.update(delta_time, red_objects)
        # Remove destroyed red objects from the scene
        for obj in destroyed:
            self._object_manager.remove_object(obj)

        # 5. Collision detection — Kiro↔Bars (with invulnerability)
        self._check_bar_collisions()

        # 6. Collision detection — Kiro↔Red objects
        self._check_red_object_collisions()

        # 7. Collision detection — Kiro↔Green objects
        self._check_green_object_collisions()

        # 8. Award points for bars that Kiro has passed
        self._check_bar_scoring()

        # 8. Check game-over condition
        if self._score_tracker.lives == 0:
            self._state = State.GAME_OVER

    # ------------------------------------------------------------------
    # Collision helpers
    # ------------------------------------------------------------------

    def _check_bar_collisions(self) -> None:
        """Kiro↔Bar collision: lose a life and activate invulnerability.

        Invulnerability timer prevents multiple life losses during the same
        collision window (Requirement 3.4).
        """
        if self._player.invulnerable_timer > 0:
            return  # currently invulnerable — skip all bar checks

        player_bounds = self._player.bounds
        for bar in self._bar_manager.active_bars:
            if rects_overlap(player_bounds, bar.bounds_top) or \
               rects_overlap(player_bounds, bar.bounds_bottom):
                # Lose a life and start invulnerability window
                self._score_tracker.lose_life()
                self._player.invulnerable_timer = self._config.player.invulnerability_duration
                # Play penalty sound
                if self._audio_service is not None:
                    self._audio_service.play_penalty()
                # Only one collision event per frame regardless of how many bars overlap
                break

    def _check_red_object_collisions(self) -> None:
        """Kiro↔Red object collision: deduct points and play penalty sound.

        Requirement 5.2: deduct penalty_points.
        Requirement 5.3: play penalty audio.
        Objects are NOT removed — they keep scrolling (only projectiles destroy them).
        """
        player_bounds = self._player.bounds
        for obj in self._object_manager.get_red_objects():
            if rects_overlap(player_bounds, obj.bounds):
                self._score_tracker.deduct_points(self._config.objects.penalty_points)
                if self._audio_service is not None:
                    self._audio_service.play_penalty()

    def _check_green_object_collisions(self) -> None:
        """Kiro↔Green object collision: add points, play bonus sound, reposition object.

        Requirement 5.4: add bonus_points.
        Requirement 5.6: play jump audio.
        After collection, reposition the object to the right edge so it can be
        collected again later (similar to how ObjectManager handles off-screen reset).
        """
        player_bounds = self._player.bounds
        for obj in self._object_manager.get_green_objects():
            if rects_overlap(player_bounds, obj.bounds):
                self._score_tracker.add_points(self._config.objects.bonus_points)
                if self._audio_service is not None:
                    self._audio_service.play_jump()
                # Reposition the green object to the right edge so it's effectively
                # "collected" and will scroll back in from the right
                obj.position.x = float(self._config.canvas.width + 50)

    def _check_bar_scoring(self) -> None:
        """Award points when Kiro's left edge passes a bar pair's right edge.

        Requirement 3.3: +points_per_bar for each pair traversed.
        The bar_manager already marks bar.scored = True via update(), but scoring
        the points is the StateManager's responsibility to avoid circular deps.
        We track scoring separately here by checking pairs that just became scored
        within this tick. To avoid double-counting we use bar.scored flag: once
        a bar is scored we do NOT call add_points here because bar_manager.update()
        already sets scored=True exactly once.

        NOTE: bar_manager.update() only sets scored=True (flag). The actual point
        award must happen the frame scored flips to True. We detect this by checking
        the flag BEFORE update vs AFTER — but since update() already ran, we check
        for bars that are scored but whose points haven't been awarded yet.

        Since we can't easily distinguish "just scored this frame" from "was already
        scored" without an extra flag, we add a `points_awarded` tracking approach:
        we use the bar's `scored` attribute directly. bar_manager.update() sets it
        to True; we read it here and award points only once by checking a separate
        per-bar attribute `_points_awarded` — but BarPair doesn't have that.

        Simpler approach: award points inside the same logic as bar_manager's
        scoring. The StateManager passes the player position to bar_manager, which
        sets bar.scored=True. We then iterate bars and award points for bars that
        just became scored. To ensure this happens exactly once, we rely on the
        fact that bar.scored starts False and only becomes True once — after which
        add_points is only ever called once for that bar.

        Implementation: iterate all active bars; if scored and not yet point-awarded,
        award points and mark as point_awarded. We extend this by tracking via a
        secondary set keyed by bar identity.
        """
        for bar in self._bar_manager.active_bars:
            if bar.scored and not getattr(bar, "_points_awarded", False):
                self._score_tracker.add_points(self._config.score.points_per_bar)
                bar._points_awarded = True  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def on_restart(self) -> None:
        """Reset all subsystems and transition to PLAYING.

        Requirement 10.4: reinitialize state with 3 lives and 0 points.
        """
        self._background.reset()
        self._player.reset()
        self._bar_manager.reset()
        self._object_manager.reset()
        self._projectile_manager.reset()
        self._score_tracker.reset()
        self._state = State.PLAYING

    def on_quit(self) -> None:
        """Close the application cleanly.

        Requirement 10.5: exit on player selection.
        """
        pygame.quit()
        sys.exit()

    def play_shoot_sound(self) -> None:
        """Play the shoot sound when a projectile is successfully fired."""
        if self._audio_service is not None:
            self._audio_service.play_shoot()
