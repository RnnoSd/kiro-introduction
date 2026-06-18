"""main.py — Flappy Kiro entry point.

Assembles all game subsystems and starts the main game loop.

Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
"""
import sys
import pygame

from src.config import GameConfig
from src.asset_loader import AssetLoader, AssetManifest
from src.audio_service import AudioService
from src.background import Background
from src.player import Player
from src.bar_manager import BarManager
from src.object_manager import ObjectManager
from src.projectile_manager import ProjectileManager
from src.score_tracker import ScoreTracker
from src.state_manager import StateManager
from src.input_handler import InputHandler
from src.game_loop import GameLoop
from src.renderer import Renderer
from src.models import Vector2


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Configuration
    # ------------------------------------------------------------------
    config = GameConfig()

    # ------------------------------------------------------------------
    # 2. Pygame initialisation — display must be created BEFORE loading
    #    assets because convert_alpha() requires an active video mode.
    # ------------------------------------------------------------------
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.display.set_mode((config.canvas.width, config.canvas.height))
    pygame.display.set_caption("Flappy Kiro")

    # ------------------------------------------------------------------
    # 3. Asset loading — FileNotFoundError for missing critical images
    # ------------------------------------------------------------------
    manifest = AssetManifest(
        images={
            "player": "assets/ghosty.png",
            "background": "img/fondo.jpg",
        },
        audio={
            "jump": "assets/jump.wav",
            "penalty": "sound/death..mp3",   # penalty/game-over sound from sound/
            "shoot": "sound/shot.mp3",        # shoot sound from sound/
            "reward": "sound/rewards.mp3",
        },
    )

    loader = AssetLoader()

    try:
        cache = loader.load(manifest)
    except FileNotFoundError as exc:
        print(f"[Flappy Kiro] ERROR: Could not load required asset — {exc}")
        print("Please make sure 'assets/ghosty.png' and 'img/example-ui.png' are present.")
        pygame.quit()
        sys.exit(1)
    except Exception as exc:
        print(f"[Flappy Kiro] Unexpected error while loading assets: {exc}")
        pygame.quit()
        sys.exit(1)

    # ------------------------------------------------------------------
    # 4. Services
    # ------------------------------------------------------------------
    audio_service = AudioService(cache)

    # ------------------------------------------------------------------
    # 5. Game objects
    # ------------------------------------------------------------------
    background = Background(
        image=cache.images["background"],
        bg_config=config.background,
        canvas_config=config.canvas,
    )

    player = Player(
        position=Vector2(x=config.player.start_x, y=config.player.start_y),
        config=config.player,
        canvas=config.canvas,
        sprite=cache.images["player"],
    )

    bar_manager = BarManager(
        bars_config=config.bars,
        canvas_config=config.canvas,
    )

    object_manager = ObjectManager(
        objects_config=config.objects,
        canvas_config=config.canvas,
    )

    projectile_manager = ProjectileManager(
        projectile_config=config.projectile,
        canvas_config=config.canvas,
    )

    score_tracker = ScoreTracker(audio_service=audio_service)

    # ------------------------------------------------------------------
    # 6. State manager (orchestrates all subsystems)
    # ------------------------------------------------------------------
    state_manager = StateManager(
        config=config,
        background=background,
        player=player,
        bar_manager=bar_manager,
        object_manager=object_manager,
        projectile_manager=projectile_manager,
        score_tracker=score_tracker,
        audio_service=audio_service,
    )

    # ------------------------------------------------------------------
    # 7. Renderer and input handler
    # ------------------------------------------------------------------
    renderer = Renderer()
    input_handler = InputHandler()

    # ------------------------------------------------------------------
    # 8. Game loop — blocks until the player quits
    # ------------------------------------------------------------------
    game_loop = GameLoop(
        config=config,
        state_manager=state_manager,
        input_handler=input_handler,
        renderer=renderer,
    )

    try:
        game_loop.start()
    except Exception as exc:
        print(f"[Flappy Kiro] Unexpected error during gameplay: {exc}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
