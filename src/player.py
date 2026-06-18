import pygame
from dataclasses import dataclass, field
from typing import Optional
from src.models import Vector2, Rect
from src.config import PlayerConfig, CanvasConfig
from src.projectile_manager import Projectile


@dataclass
class Player:
    """Kiro the ghost player character."""
    position: Vector2
    config: PlayerConfig
    canvas: CanvasConfig
    sprite: Optional[pygame.Surface] = field(default=None)

    # Ability state
    is_braking: bool = False
    brake_timer: float = 0.0          # seconds remaining of active brake
    cooldown_shoot: float = 0.0       # seconds remaining on shoot cooldown
    cooldown_dash: float = 0.0        # seconds remaining on dash cooldown
    cooldown_brake: float = 0.0       # seconds remaining on brake cooldown
    invulnerable_timer: float = 0.0   # seconds remaining of invulnerability

    @property
    def bounds(self) -> Rect:
        """Current AABB bounding box."""
        return Rect(
            x=self.position.x,
            y=self.position.y,
            width=self.config.sprite_width,
            height=self.config.sprite_height,
        )

    def update(self, delta_time: float, movement_vector: tuple, boost_active: bool) -> None:
        """Apply movement according to input; respect brake state and canvas bounds."""
        # Decrement all timers
        self.brake_timer = max(0.0, self.brake_timer - delta_time)
        self.cooldown_shoot = max(0.0, self.cooldown_shoot - delta_time)
        self.cooldown_dash = max(0.0, self.cooldown_dash - delta_time)
        self.cooldown_brake = max(0.0, self.cooldown_brake - delta_time)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - delta_time)

        # Update brake state: clear once timer expires
        if self.brake_timer <= 0.0:
            self.is_braking = False

        # No movement while braking
        if self.is_braking:
            return

        dx, dy = movement_vector
        speed = self.config.boost_speed if boost_active else self.config.base_speed

        # Apply movement independently on each axis (supports diagonal movement)
        self.position.x += dx * speed
        self.position.y += dy * speed

        # Clamp to canvas bounds
        self.position.x = max(0.0, min(self.position.x, self.canvas.width - self.config.sprite_width))
        self.position.y = max(0.0, min(self.position.y, self.canvas.height - self.config.sprite_height))

    def try_shoot(self) -> Optional[Projectile]:
        """If cooldown expired, create a projectile at the player's right edge and
        activate the 500 ms shoot cooldown. Returns None if still on cooldown."""
        if self.cooldown_shoot > 0.0:
            return None
        proj_x = self.position.x + self.config.sprite_width
        proj_y = self.position.y + (self.config.sprite_height // 2) - 3  # vertically centered
        projectile = Projectile(
            position=Vector2(x=proj_x, y=proj_y),
            bounds=Rect(x=proj_x, y=proj_y, width=20, height=6),
        )
        self.cooldown_shoot = self.config.cooldown_shoot  # 0.5 s
        return projectile

    def try_dash_back(self) -> None:
        """If cooldown expired, move X -100 px (min 0) and activate the 1000 ms dash cooldown."""
        if self.cooldown_dash > 0.0:
            return
        self.position.x = max(0.0, self.position.x - self.config.dash_distance)
        self.cooldown_dash = self.config.cooldown_dash  # 1.0 s

    def try_brake(self) -> None:
        """If cooldown expired, activate brake for 3 s and set the 5000 ms brake cooldown."""
        if self.cooldown_brake > 0.0:
            return
        self.is_braking = True
        self.brake_timer = self.config.brake_duration  # 3.0 s
        self.cooldown_brake = self.config.cooldown_brake  # 5.0 s

    def render(self, surface: pygame.Surface) -> None:
        """Draw the sprite scaled to sprite_width×sprite_height, or a placeholder rect."""
        if self.sprite is not None:
            scaled = pygame.transform.scale(
                self.sprite,
                (self.config.sprite_width, self.config.sprite_height)
            )
            surface.blit(scaled, (int(self.position.x), int(self.position.y)))
        else:
            pygame.draw.rect(surface, (255, 255, 255), (
                int(self.position.x), int(self.position.y),
                self.config.sprite_width, self.config.sprite_height
            ))

    def reset(self) -> None:
        """Restore initial position and clear all cooldowns."""
        self.position.x = self.config.start_x
        self.position.y = self.config.start_y
        self.is_braking = False
        self.brake_timer = 0.0
        self.cooldown_shoot = 0.0
        self.cooldown_dash = 0.0
        self.cooldown_brake = 0.0
        self.invulnerable_timer = 0.0
