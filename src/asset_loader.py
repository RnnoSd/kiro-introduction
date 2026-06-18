from dataclasses import dataclass, field
from typing import Dict
import pygame
import os


@dataclass
class AssetManifest:
    images: Dict[str, str]  # {"player": "assets/ghosty.png", "background": "img/example-ui.png"}
    audio: Dict[str, str]   # {"jump": "assets/jump.wav", "penalty": "assets/game_over.wav"}


@dataclass
class AssetCache:
    images: Dict[str, pygame.Surface] = field(default_factory=dict)
    audio: Dict[str, object] = field(default_factory=dict)  # pygame.mixer.Sound or None


class AssetLoader:
    def load(self, manifest: AssetManifest) -> AssetCache:
        """Load all assets. Raises FileNotFoundError if a critical image is missing."""
        cache = AssetCache()

        # Load images — raise FileNotFoundError for missing critical images
        for key, path in manifest.images.items():
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Required image asset not found: '{path}'. "
                    f"Make sure '{path}' exists in the project root."
                )
            surface = pygame.image.load(path)
            # JPEGs have no alpha channel — use convert() to avoid errors
            ext = os.path.splitext(path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                cache.images[key] = surface.convert()
            else:
                cache.images[key] = surface.convert_alpha()

        # Load audio — silent failure per file (graceful degradation per Req 9.4, 9.5)
        for key, path in manifest.audio.items():
            try:
                cache.audio[key] = pygame.mixer.Sound(path)
            except Exception:
                cache.audio[key] = None  # graceful degradation: disable only this sound

        return cache


# Default manifest for the Flappy Kiro game
DEFAULT_MANIFEST = AssetManifest(
    images={
        "player": "assets/ghosty.png",
        "background": "img/example-ui.png",
    },
    audio={
        "jump": "assets/jump.wav",
        "penalty": "assets/game_over.wav",
    },
)
