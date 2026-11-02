"""
Sound system and audio manager for Not-a-Doom.
Loads external sound files (MP3, WAV, OGG) from assets/sound/
or falls back to procedural retro audio synthesis.
"""
import os
import wave
import numpy as np
import pygame

ASSETS_SOUND_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sound")
SAMPLE_RATE = 44100


def save_wav(filename: str, samples: np.ndarray):
    """Save 16-bit mono PCM samples to WAV file."""
    os.makedirs(ASSETS_SOUND_DIR, exist_ok=True)
    filepath = os.path.join(ASSETS_SOUND_DIR, filename)
    samples = np.clip(samples, -1.0, 1.0)
    int16_data = (samples * 32767).astype(np.int16)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16_data.tobytes())
    return filepath


def synthesize_shotgun_blast() -> np.ndarray:
    """Procedural fallback shotgun blast."""
    duration = 0.55
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, total_samples)
    freq = 120 * np.exp(-t * 12) + 35
    boom = np.sin(2 * np.pi * freq * t)
    crack = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 25)
    env = np.exp(-t * 8.5)
    env[: int(0.005 * SAMPLE_RATE)] = np.linspace(0.1, 1.0, int(0.005 * SAMPLE_RATE))
    raw = (noise * 0.75 + boom * 0.85 + crack * 0.4) * env
    return np.tanh(raw * 2.8)


def synthesize_shotgun_pump() -> np.ndarray:
    """Procedural fallback pump sound."""
    duration = 0.32
    total_samples = int(SAMPLE_RATE * duration)
    samples = np.zeros(total_samples, dtype=np.float32)

    def add_click(start_time: float, freq1: float, freq2: float, decay: float, vol: float):
        start_idx = int(start_time * SAMPLE_RATE)
        sub_len = int(0.07 * SAMPLE_RATE)
        if start_idx + sub_len > total_samples:
            sub_len = total_samples - start_idx
        sub_t = np.linspace(0, sub_len / SAMPLE_RATE, sub_len, endpoint=False)
        tone = (np.sin(2 * np.pi * freq1 * sub_t) + 0.5 * np.sin(2 * np.pi * freq2 * sub_t))
        noise = np.random.uniform(-0.6, 0.6, sub_len)
        env = np.exp(-sub_t * decay)
        samples[start_idx : start_idx + sub_len] += (tone * 0.6 + noise * 0.4) * env * vol

    add_click(start_time=0.03, freq1=1900, freq2=850, decay=75, vol=0.8)
    add_click(start_time=0.18, freq1=1400, freq2=550, decay=60, vol=0.95)
    return np.tanh(samples * 1.8)


def synthesize_footstep() -> np.ndarray:
    """Soft, gentle, realistic boot scuff/tap on stone (no harsh kick-drum boom)."""
    duration = 0.08
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    # Subtle low frequency brush without loud resonant sub-bass
    noise = np.random.uniform(-0.15, 0.15, total_samples)
    # Quick exponential decay
    env = np.exp(-t * 60)
    return noise * env * 0.35


class SoundManager:
    """Manages audio playback, external audio loading, and fallback synthesis."""
    def __init__(self, game):
        self.game = game
        self.enabled = False
        self.has_integrated_pump = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.enabled = True
        except Exception as e:
            print(f"Warning: Audio device initialization failed: {e}")

        self.sounds = {}
        if self.enabled:
            self._init_sounds()

    def _find_audio_file(self, base_name: str):
        """Check for existing MP3, WAV or OGG files."""
        for ext in [".mp3", ".wav", ".ogg"]:
            path = os.path.join(ASSETS_SOUND_DIR, base_name + ext)
            if os.path.exists(path):
                return path
        return None

    def _init_sounds(self):
        # 1. Shotgun Sound: prioritize user's shotgun_sound.mp3
        user_sound = self._find_audio_file("shotgun_sound")
        if user_sound:
            self.sounds["shot"] = pygame.mixer.Sound(user_sound)
            self.has_integrated_pump = True
        else:
            shot_file = self._find_audio_file("shotgun_shot")
            if not shot_file:
                shot_file = save_wav("shotgun_shot.wav", synthesize_shotgun_blast())
            self.sounds["shot"] = pygame.mixer.Sound(shot_file)
            self.has_integrated_pump = False

        self.sounds["shot"].set_volume(0.9)

        # 2. Pump sound (only needed if shot doesn't have integrated pump)
        pump_file = self._find_audio_file("shotgun_pump")
        if not pump_file:
            pump_file = save_wav("shotgun_pump.wav", synthesize_shotgun_pump())
        self.sounds["pump"] = pygame.mixer.Sound(pump_file)
        self.sounds["pump"].set_volume(0.75)

        # 3. Soft muffled footstep (calm, low volume)
        step_path = os.path.join(ASSETS_SOUND_DIR, "footstep.wav")
        # Regenerate with soft synthesis
        save_wav("footstep.wav", synthesize_footstep())
        self.sounds["step"] = pygame.mixer.Sound(step_path)
        self.sounds["step"].set_volume(0.12)  # Soft background volume

    def play_shot(self):
        if self.enabled and "shot" in self.sounds:
            self.sounds["shot"].play()

    def play_pump(self):
        if self.enabled and not self.has_integrated_pump and "pump" in self.sounds:
            self.sounds["pump"].play()

    def play_step(self):
        if self.enabled and "step" in self.sounds:
            self.sounds["step"].play()
