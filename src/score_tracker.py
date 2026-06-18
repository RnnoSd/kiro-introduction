import pygame
from typing import Optional


class ScoreTracker:
    """Manages score, lives, and bonus logic.

    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
    """

    MAX_LIVES = 9
    INITIAL_LIVES = 3
    LIFE_BONUS_THRESHOLD = 1000
    REWARD_THRESHOLD = 300

    def __init__(self, audio_service=None):
        self.score: int = 0
        self.lives: int = self.INITIAL_LIVES
        self._last_bonus_threshold: int = 0
        self._last_reward_threshold: int = 0
        self._audio_service = audio_service  # Optional AudioService

    def add_points(self, amount: int) -> None:
        """Add points, play reward audio every 300 points, and grant a life bonus every 1000 points.

        Requirement 4.4: +5 pts per bar pair, +100 pts per green object.
        Requirement 4.5: bonus life every 1000 points, exactly once per threshold, max 9.
        Reward audio plays every 300 points milestone.
        """
        self.score += amount

        # Check if we crossed any new 300-point reward threshold
        new_reward_threshold = (self.score // self.REWARD_THRESHOLD) * self.REWARD_THRESHOLD
        if new_reward_threshold > self._last_reward_threshold:
            if self._audio_service is not None:
                self._audio_service.play_reward()
            self._last_reward_threshold = new_reward_threshold

        # Check if we crossed any new 1000-point threshold
        new_threshold = (self.score // self.LIFE_BONUS_THRESHOLD) * self.LIFE_BONUS_THRESHOLD
        if new_threshold > self._last_bonus_threshold:
            if self.lives < self.MAX_LIVES:
                self.lives = min(self.MAX_LIVES, self.lives + 1)
                if self._audio_service is not None:
                    self._audio_service.play_jump()
            # Update tracking regardless of whether a life was granted
            self._last_bonus_threshold = new_threshold

    def deduct_points(self, amount: int) -> None:
        """Deduct points; if score reaches 0 or below, fix at 0 and lose a life.

        Requirement 4.3: -20 pts per red object collision.
        Requirement 4.1: score minimum is always 0.
        Requirement 4.6: lose a life when score hits 0 due to penalty.
        """
        if self.score <= 0:
            # Score is already 0; just lose a life
            self.lose_life()
            return
        self.score -= amount
        if self.score <= 0:
            self.score = 0
            self.lose_life()

    def lose_life(self) -> None:
        """Decrement lives by 1 (minimum 0).

        Requirement 4.2: lives floor is 0.
        """
        self.lives = max(0, self.lives - 1)

    def reset(self) -> None:
        """Reset to initial state: score=0, lives=3, threshold=0.

        Requirement 4.7: full reset on game restart.
        """
        self.score = 0
        self.lives = self.INITIAL_LIVES
        self._last_bonus_threshold = 0
        self._last_reward_threshold = 0

    def render(self, surface: pygame.Surface) -> None:
        """Draw HUD: score and lives at a fixed position.

        Requirement 4.6: display score and lives on screen.
        """
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        surface.blit(score_text, (10, 10))
        surface.blit(lives_text, (10, 50))
