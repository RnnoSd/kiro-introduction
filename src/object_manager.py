import pygame
import random
from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto

from src.models import Vector2, Rect
from src.config import ObjectsConfig, CanvasConfig


class ObjectType(Enum):
    RED = auto()
    GREEN = auto()


@dataclass
class GameObject:
    obj_type: ObjectType
    position: Vector2
    speed: float  # px/frame, between 3 and 8
    size: int = 30

    @property
    def bounds(self) -> Rect:
        return Rect(
            x=self.position.x,
            y=self.position.y,
            width=self.size,
            height=self.size,
        )


class ObjectManager:
    def __init__(self, objects_config: ObjectsConfig, canvas_config: CanvasConfig):
        self._config = objects_config
        self._canvas = canvas_config
        self.active_objects: List[GameObject] = []
        self._initialize_objects()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_speed(self) -> float:
        return random.uniform(self._config.speed_min, self._config.speed_max)

    def _random_y(self) -> float:
        return random.uniform(0, self._canvas.height - self._config.size)

    def _random_x_offscreen(self) -> float:
        """Return an X position beyond the right edge of the canvas."""
        return float(self._canvas.width + random.randint(0, 200))

    def _initialize_objects(self) -> None:
        """Create at least 1 RED and 1 GREEN object with random positions and speeds."""
        # Red object — staggered start so they don't overlap at launch
        self.active_objects.append(
            GameObject(
                obj_type=ObjectType.RED,
                position=Vector2(x=self._random_x_offscreen(), y=self._random_y()),
                speed=self._random_speed(),
                size=self._config.size,
            )
        )
        # Green object — placed 400 px further right for a natural spread
        self.active_objects.append(
            GameObject(
                obj_type=ObjectType.GREEN,
                position=Vector2(
                    x=self._random_x_offscreen() + 400, y=self._random_y()
                ),
                speed=self._random_speed(),
                size=self._config.size,
            )
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, delta_time: float) -> None:
        """Move each object at its own speed (px/frame).

        When an object exits through the left edge it is repositioned at the
        right edge with a new random Y coordinate.
        """
        for obj in self.active_objects:
            obj.position.x -= obj.speed  # speed is px/frame, not px/s
            if obj.position.x + obj.size <= 0:
                obj.position.x = float(self._canvas.width)
                obj.position.y = self._random_y()

    def render(self, surface: pygame.Surface) -> None:
        """Draw each object as a filled square — red for RED, green for GREEN."""
        for obj in self.active_objects:
            color = (220, 50, 50) if obj.obj_type == ObjectType.RED else (50, 200, 50)
            pygame.draw.rect(
                surface,
                color,
                (int(obj.position.x), int(obj.position.y), obj.size, obj.size),
            )

    def reset(self) -> None:
        """Reinitialise all objects to fresh random positions and speeds."""
        self.active_objects.clear()
        self._initialize_objects()

    # ------------------------------------------------------------------
    # Accessors used by other systems
    # ------------------------------------------------------------------

    def get_red_objects(self) -> List[GameObject]:
        """Return all active RED objects (used by ProjectileManager for collision)."""
        return [o for o in self.active_objects if o.obj_type == ObjectType.RED]

    def get_green_objects(self) -> List[GameObject]:
        """Return all active GREEN objects."""
        return [o for o in self.active_objects if o.obj_type == ObjectType.GREEN]

    def remove_object(self, obj: GameObject) -> None:
        """Remove an object from the active list (e.g., destroyed by a projectile).

        Rather than permanently deleting it, the object is repositioned off-screen
        so that there is always at least 1 RED and 1 GREEN object visible.
        """
        if obj in self.active_objects:
            obj.position.x = float(self._canvas.width + 200)
            obj.position.y = self._random_y()
