import pygame
from dataclasses import dataclass
from typing import List
from src.models import Vector2, Rect, rects_overlap
from src.config import ProjectileConfig, CanvasConfig


@dataclass
class Projectile:
    """A projectile fired by the player, traveling to the right at a fixed speed."""
    position: Vector2
    bounds: Rect
    speed: float = 400.0  # px/s toward the right


class ProjectileManager:
    """Manages all active projectiles: spawning, movement, collision, and rendering."""

    def __init__(self, projectile_config: ProjectileConfig, canvas_config: CanvasConfig):
        self._config = projectile_config
        self._canvas = canvas_config
        self.active_projectiles: List[Projectile] = []

    def spawn(self, origin: Vector2) -> None:
        """Instantiate a projectile at the given origin position (right edge of Kiro's sprite)."""
        proj = Projectile(
            position=Vector2(x=origin.x, y=origin.y),
            bounds=Rect(
                x=origin.x,
                y=origin.y,
                width=self._config.width,
                height=self._config.height,
            ),
            speed=self._config.speed,
        )
        self.active_projectiles.append(proj)

    def update(self, delta_time: float, red_objects: list) -> list:
        """Move projectiles right at 400 px/s; detect collision with red objects;
        remove both projectile and red object on hit in the same frame.
        Remove projectiles that exit the right canvas edge.
        Returns list of red objects that were destroyed."""
        displacement = self._config.speed * delta_time
        projectiles_to_remove = set()
        objects_to_remove = set()
        destroyed_objects = []

        for i, proj in enumerate(self.active_projectiles):
            proj.position.x += displacement
            proj.bounds.x = proj.position.x

            # Remove if out of canvas right edge
            if proj.position.x >= self._canvas.width:
                projectiles_to_remove.add(i)
                continue

            # Check collision with each red object (only those not already destroyed)
            for obj in red_objects:
                if obj not in objects_to_remove and rects_overlap(proj.bounds, obj.bounds):
                    projectiles_to_remove.add(i)
                    objects_to_remove.add(obj)
                    destroyed_objects.append(obj)
                    break  # one projectile can only destroy one object

        # Rebuild list without removed projectiles
        self.active_projectiles = [
            p for i, p in enumerate(self.active_projectiles)
            if i not in projectiles_to_remove
        ]

        return destroyed_objects

    def render(self, surface: pygame.Surface) -> None:
        """Draw all active projectiles as yellow horizontal bars."""
        YELLOW = (255, 255, 0)
        for proj in self.active_projectiles:
            pygame.draw.rect(surface, YELLOW, (
                int(proj.position.x), int(proj.position.y),
                self._config.width, self._config.height,
            ))

    def reset(self) -> None:
        """Remove all active projectiles."""
        self.active_projectiles.clear()
