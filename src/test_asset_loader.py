"""Unit tests for AssetLoader (src/asset_loader.py).

These tests exercise the loading logic without a display — pygame.init() is NOT
called, so we patch the parts that need a display or mixer at the module level.
"""
import os
import pytest
import unittest.mock as mock

from src.asset_loader import AssetManifest, AssetCache, AssetLoader, DEFAULT_MANIFEST


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _manifest_with(images=None, audio=None):
    return AssetManifest(
        images=images or {},
        audio=audio or {},
    )


# ---------------------------------------------------------------------------
# AssetManifest
# ---------------------------------------------------------------------------

class TestAssetManifest:
    def test_stores_images_and_audio(self):
        m = AssetManifest(
            images={"player": "assets/ghosty.png"},
            audio={"jump": "assets/jump.wav"},
        )
        assert m.images == {"player": "assets/ghosty.png"}
        assert m.audio == {"jump": "assets/jump.wav"}


# ---------------------------------------------------------------------------
# DEFAULT_MANIFEST
# ---------------------------------------------------------------------------

class TestDefaultManifest:
    def test_player_image_key(self):
        assert "player" in DEFAULT_MANIFEST.images
        assert DEFAULT_MANIFEST.images["player"] == "assets/ghosty.png"

    def test_background_image_key(self):
        assert "background" in DEFAULT_MANIFEST.images
        assert DEFAULT_MANIFEST.images["background"] == "img/example-ui.png"

    def test_jump_audio_key(self):
        assert "jump" in DEFAULT_MANIFEST.audio
        assert DEFAULT_MANIFEST.audio["jump"] == "assets/jump.wav"

    def test_penalty_audio_key(self):
        assert "penalty" in DEFAULT_MANIFEST.audio
        assert DEFAULT_MANIFEST.audio["penalty"] == "assets/game_over.wav"


# ---------------------------------------------------------------------------
# AssetCache
# ---------------------------------------------------------------------------

class TestAssetCache:
    def test_default_empty_dicts(self):
        cache = AssetCache()
        assert cache.images == {}
        assert cache.audio == {}


# ---------------------------------------------------------------------------
# AssetLoader.load — image loading
# ---------------------------------------------------------------------------

class TestAssetLoaderImages:
    def test_raises_file_not_found_for_missing_image(self, tmp_path):
        """FileNotFoundError must be raised when a required image is absent."""
        manifest = _manifest_with(images={"player": str(tmp_path / "missing.png")})
        loader = AssetLoader()
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load(manifest)
        assert "missing.png" in str(exc_info.value)

    def test_error_message_contains_path(self, tmp_path):
        path = str(tmp_path / "ghosty.png")
        manifest = _manifest_with(images={"player": path})
        loader = AssetLoader()
        with pytest.raises(FileNotFoundError, match=path):
            loader.load(manifest)

    def test_loads_image_into_cache(self, tmp_path):
        """A valid image file should be loaded and stored in cache.images."""
        # Create a minimal 1x1 PNG so the file actually exists
        import pygame
        pygame.display.init()
        surf = pygame.Surface((1, 1))
        img_path = str(tmp_path / "test.png")
        pygame.image.save(surf, img_path)

        fake_surface = mock.MagicMock(spec=pygame.Surface)
        with mock.patch("pygame.image.load") as mock_load:
            mock_load.return_value.convert_alpha.return_value = fake_surface
            loader = AssetLoader()
            cache = loader.load(_manifest_with(images={"player": img_path}))

        assert cache.images["player"] is fake_surface
        mock_load.assert_called_once_with(img_path)

    def test_raises_for_second_missing_image_when_first_exists(self, tmp_path):
        """FileNotFoundError raised for the first missing image in iteration order."""
        existing = tmp_path / "exists.png"
        existing.write_bytes(b"")  # dummy file, won't be loaded by pygame in this branch

        # Patch os.path.exists so the first path returns True, second returns False
        missing_path = str(tmp_path / "missing.png")
        existing_path = str(existing)

        def fake_exists(path):
            return path == existing_path

        fake_surface = mock.MagicMock()
        with mock.patch("os.path.exists", side_effect=fake_exists), \
             mock.patch("pygame.image.load") as mock_load:
            mock_load.return_value.convert_alpha.return_value = fake_surface
            loader = AssetLoader()
            with pytest.raises(FileNotFoundError):
                loader.load(_manifest_with(images={
                    "background": existing_path,
                    "player": missing_path,
                }))


# ---------------------------------------------------------------------------
# AssetLoader.load — audio loading (graceful degradation)
# ---------------------------------------------------------------------------

class TestAssetLoaderAudio:
    def test_audio_none_when_file_missing(self, tmp_path):
        """Missing audio should silently set the cache entry to None."""
        missing_wav = str(tmp_path / "missing.wav")
        manifest = _manifest_with(audio={"jump": missing_wav})
        loader = AssetLoader()
        with mock.patch("pygame.mixer.Sound", side_effect=FileNotFoundError("not found")):
            cache = loader.load(manifest)
        assert cache.audio["jump"] is None

    def test_audio_none_when_mixer_unavailable(self):
        """Any exception from pygame.mixer.Sound should be swallowed."""
        manifest = _manifest_with(audio={"jump": "assets/jump.wav"})
        loader = AssetLoader()
        with mock.patch("pygame.mixer.Sound", side_effect=Exception("mixer not init")):
            cache = loader.load(manifest)
        assert cache.audio["jump"] is None

    def test_one_audio_failure_does_not_affect_other(self, tmp_path):
        """Failure loading one audio file must not prevent loading another."""
        good_wav = str(tmp_path / "good.wav")

        fake_sound = mock.MagicMock()

        def side_effect(path):
            if path == good_wav:
                return fake_sound
            raise FileNotFoundError(f"not found: {path}")

        manifest = _manifest_with(audio={"bad": "missing.wav", "good": good_wav})
        loader = AssetLoader()
        with mock.patch("pygame.mixer.Sound", side_effect=side_effect):
            cache = loader.load(manifest)

        assert cache.audio["bad"] is None
        assert cache.audio["good"] is fake_sound

    def test_successful_audio_loaded_into_cache(self, tmp_path):
        """Successfully loaded audio should be stored in cache.audio."""
        wav_path = str(tmp_path / "jump.wav")
        fake_sound = mock.MagicMock()
        manifest = _manifest_with(audio={"jump": wav_path})
        loader = AssetLoader()
        with mock.patch("pygame.mixer.Sound", return_value=fake_sound):
            cache = loader.load(manifest)
        assert cache.audio["jump"] is fake_sound

    def test_empty_manifest_returns_empty_cache(self):
        """An empty manifest should return an empty AssetCache without errors."""
        loader = AssetLoader()
        cache = loader.load(_manifest_with())
        assert cache.images == {}
        assert cache.audio == {}
