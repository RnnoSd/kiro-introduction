import pygame
from typing import Set, List, Tuple


class InputHandler:
    """Translates pygame events into game actions and movement vectors."""

    def __init__(self):
        self.keys_held: Set[int] = set()

    def process_events(self, events: list) -> List[str]:
        """
        Process pygame events. Updates keys_held and returns list of discrete actions.

        Discrete actions (fired on KEYDOWN only):
          'shoot'   — A key
          'dash'    — W key
          'brake'   — S key
          'restart' — ENTER key
          'quit'    — ESC key or window close (pygame.QUIT)
        """
        actions: List[str] = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_held.add(event.key)
                if event.key == pygame.K_a:
                    actions.append('shoot')
                elif event.key == pygame.K_w:
                    actions.append('dash')
                elif event.key == pygame.K_s:
                    actions.append('brake')
                elif event.key == pygame.K_RETURN:
                    actions.append('restart')
                elif event.key == pygame.K_ESCAPE:
                    actions.append('quit')
            elif event.type == pygame.KEYUP:
                self.keys_held.discard(event.key)
            elif event.type == pygame.QUIT:
                actions.append('quit')
        return actions

    def get_movement_vector(self) -> Tuple[int, int]:
        """
        Returns (dx, dy) based on arrow keys currently held.
        Each axis value is in {-1, 0, 1}.
        LEFT/RIGHT control dx; UP/DOWN control dy (UP = -1, DOWN = +1).
        """
        dx = 0
        dy = 0
        if pygame.K_LEFT in self.keys_held:
            dx -= 1
        if pygame.K_RIGHT in self.keys_held:
            dx += 1
        if pygame.K_UP in self.keys_held:
            dy -= 1
        if pygame.K_DOWN in self.keys_held:
            dy += 1
        return (dx, dy)

    def is_boost_active(self) -> bool:
        """Returns True if SPACE is currently held."""
        return pygame.K_SPACE in self.keys_held
