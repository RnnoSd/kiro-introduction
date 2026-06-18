import pygame
import random
from dataclasses import dataclass, field
from typing import List, Optional

from src.models import Rect
from src.config import BarsConfig, CanvasConfig


@dataclass
class BarPair:
    x: float
    gap_y: float       # Y coordinate of gap center
    gap_size: float    # height of gap in pixels (150–200)
    bar_width: float   # width of the bar column in pixels
    scored: bool = False

    @property
    def bounds_top(self) -> Rect:
        """Bounding box of the top bar."""
        top_height = self.gap_y - self.gap_size / 2
        return Rect(x=self.x, y=0.0, width=self.bar_width, height=max(0.0, top_height))

    @property
    def bounds_bottom(self) -> Rect:
        """Bounding box of the bottom bar (extends arbitrarily downward)."""
        bottom_y = self.gap_y + self.gap_size / 2
        return Rect(x=self.x, y=bottom_y, width=self.bar_width, height=600.0)


class BarManager:
    def __init__(self, bars_config: BarsConfig, canvas_config: CanvasConfig):
        self._config = bars_config
        self._canvas = canvas_config
        self.active_bars: List[BarPair] = []
        # Spawn initial bar at the right edge of the canvas
        self._spawn_bar()

    def _spawn_bar(self) -> None:
        gap_y = random.uniform(self._config.min_gap_y, self._config.max_gap_y)
        gap_size = random.uniform(self._config.gap_size_min, self._config.gap_size_max)
        self.active_bars.append(BarPair(
            x=float(self._canvas.width),
            gap_y=gap_y,
            gap_size=gap_size,
            bar_width=float(self._config.width),
        ))

    def update(self, delta_time: float, player_left_x: Optional[float] = None) -> None:
        """Move bars left; spawn new pair when rightmost is far enough; remove off-screen pairs."""
        displacement = self._config.scroll_speed * delta_time

        for bar in self.active_bars:
            bar.x -= displacement
            # Mark scored when player's left edge passes the bar's right edge
            if player_left_x is not None and not bar.scored:
                if player_left_x > bar.x + self._config.width:
                    bar.scored = True

        # Remove bars that are completely off screen (right edge <= 0)
        self.active_bars = [
            b for b in self.active_bars if b.x + self._config.width > 0
        ]

        # Spawn new bar if there are none or if rightmost is far enough from right edge
        if not self.active_bars:
            self._spawn_bar()
        else:
            rightmost_x = max(b.x for b in self.active_bars)
            distance_to_right = self._canvas.width - (rightmost_x + self._config.width)
            if distance_to_right >= self._config.spawn_distance:
                self._spawn_bar()

    def render(self, surface: pygame.Surface) -> None:
        """Draw all bars in green."""
        GREEN = (0, 200, 0)
        for bar in self.active_bars:
            # Top bar
            top_h = bar.gap_y - bar.gap_size / 2
            if top_h > 0:
                pygame.draw.rect(
                    surface, GREEN,
                    (int(bar.x), 0, self._config.width, int(top_h))
                )
            # Bottom bar
            bottom_y = bar.gap_y + bar.gap_size / 2
            bottom_h = self._canvas.height - bottom_y
            if bottom_h > 0:
                pygame.draw.rect(
                    surface, GREEN,
                    (int(bar.x), int(bottom_y), self._config.width, int(bottom_h))
                )

    def reset(self) -> None:
        """Remove all active bar pairs and spawn a fresh initial one."""
        self.active_bars = []
        self._spawn_bar()
