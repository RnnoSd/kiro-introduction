class AudioService:
    """Wraps pygame.mixer with graceful degradation when audio is unavailable.

    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    """

    def __init__(self, asset_cache):
        """
        asset_cache: AssetCache from AssetLoader
        cache.audio["jump"]    -> pygame.mixer.Sound or None
        cache.audio["penalty"] -> pygame.mixer.Sound or None
        """
        self._jump_sound = asset_cache.audio.get("jump")
        self._penalty_sound = asset_cache.audio.get("penalty")

    def play_jump(self) -> None:
        """Reproduce jump.wav (bonus de vida). Silent if not available.

        Requirement 9.2: plays jump.wav when the player gains a life bonus.
        Requirement 9.4: if jump.wav was not loaded, does nothing without raising.
        """
        if self._jump_sound is not None:
            try:
                self._jump_sound.play()
            except Exception:
                # Disable only this sound permanently; the other continues working
                self._jump_sound = None

    def play_penalty(self) -> None:
        """Reproduce game_over.wav (colisión con Objeto_Rojo). Silent if not available.

        Requirement 9.3: plays game_over.wav on collision with a red object.
        Requirement 9.5: if game_over.wav was not loaded, does nothing without raising.
        """
        if self._penalty_sound is not None:
            try:
                self._penalty_sound.play()
            except Exception:
                # Disable only this sound permanently; the other continues working
                self._penalty_sound = None
