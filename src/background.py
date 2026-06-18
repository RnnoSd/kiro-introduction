import pygame
from src.config import BackgroundConfig, CanvasConfig


class Background:
    """Infinite scrolling background using double-buffer technique.

    Two copies of the background image are positioned consecutively and scrolled
    to the left at a constant speed. When a copy fully exits the left edge, it is
    immediately repositioned behind the other copy so the scroll is seamless.

    The scroll speed is independent of the Player's brake state — the background
    always scrolls regardless of which abilities are active.
    """

    def __init__(
        self,
        image: pygame.Surface,
        bg_config: BackgroundConfig,
        canvas_config: CanvasConfig,
    ) -> None:
        self._scroll_speed = bg_config.scroll_speed  # px/s
        self._canvas_width = canvas_config.width
        self._canvas_height = canvas_config.height

        # Scale image to canvas size if needed so both copies fill the screen
        img_w, img_h = image.get_size()
        if img_w != canvas_config.width or img_h != canvas_config.height:
            self._image = pygame.transform.scale(
                image, (canvas_config.width, canvas_config.height)
            )
        else:
            self._image = image

        # Copy 1 starts at the left edge; copy 2 is immediately to the right
        self._x1: float = 0.0
        self._x2: float = float(canvas_config.width)

        # Total scroll distance accumulated — useful for property-based tests
        self.scroll_x: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, delta_time: float) -> None:
        """Advance scroll; reposition whichever copy exits the left edge."""
        displacement = self._scroll_speed * delta_time
        self.scroll_x += displacement

        self._x1 -= displacement
        self._x2 -= displacement

        # When a copy has scrolled completely off the left edge, move it just
        # behind the other copy so there is never a visible gap.
        if self._x1 + self._canvas_width <= 0:
            self._x1 = self._x2 + self._canvas_width
        if self._x2 + self._canvas_width <= 0:
            self._x2 = self._x1 + self._canvas_width

    def render(self, surface: pygame.Surface) -> None:
        """Draw both background copies without any visible gap."""
        surface.blit(self._image, (int(self._x1), 0))
        surface.blit(self._image, (int(self._x2), 0))

    def reset(self) -> None:
        """Restore initial scroll positions."""
        self._x1 = 0.0
        self._x2 = float(self._canvas_width)
        self.scroll_x = 0.0

    # ------------------------------------------------------------------
    # Testing helpers
    # ------------------------------------------------------------------

    def get_positions(self) -> tuple[float, float]:
        """Return current (x1, x2) positions — used by tests."""
        return (self._x1, self._x2)
