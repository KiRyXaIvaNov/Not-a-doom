"""
Sound system and procedural retro audio synthesizer for Not-a-Doom.
Generates punchy 16-bit sound effects (shotgun blast, pump action, footsteps)
and saves/loads them as standard WAV files in assets/sound/.
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
    # Clamp and convert to int16
    samples = np.clip(samples, -1.0, 1.0)
    int16_data = (samples * 32767).astype(np.int16)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16_data.tobytes())
    return filepath


def synthesize_shotgun_blast() -> np.ndarray:
    """Synthesize high-impact retro DOOM shotgun blast with explosion transient and crunchy decay."""
    duration = 0.55
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # 1. White noise explosion burst
    noise = np.random.uniform(-1.0, 1.0, total_samples)

    # 2. Heavy sub-bass pitch drop (120 Hz dropping to 35 Hz)
    freq = 120 * np.exp(-t * 12) + 35
    boom = np.sin(2 * np.pi * freq * t)

    # 3. Mid-frequency crack
    crack = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 25)

    # 4. Multi-stage exponential envelope
    # Instant attack (0.005s) followed by steep decay and low-frequency rumble
    env = np.exp(-t * 8.5)
    env[: int(0.005 * SAMPLE_RATE)] = np.linspace(0.1, 1.0, int(0.005 * SAMPLE_RATE))

    # Combine signals
    raw = (noise * 0.75 + boom * 0.85 + crack * 0.4) * env

    # Overdrive / soft-clipping for visceral vintage distortion
    clipped = np.tanh(raw * 2.8)
    return clipped


def synthesize_shotgun_pump() -> np.ndarray:
    """Synthesize mechanical metallic pump action (two sequential click-clack sounds)."""
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

    # Click 1: Slide back (mechanical snap)
    add_click(start_time=0.03, freq1=1900, freq2=850, decay=75, vol=0.8)
    # Click 2: Slide forward (heavy lock)
    add_click(start_time=0.18, freq1=1400, freq2=550, decay=60, vol=0.95)

    return np.tanh(samples * 1.8)


def synthesize_footstep() -> np.ndarray:
    """Synthesize low muffled boot step impact."""
    duration = 0.1
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    boom = np.sin(2 * np.pi * 65 * t)
    noise = np.random.uniform(-0.3, 0.3, total_samples)
    env = np.exp(-t * 35)
    return (boom * 0.7 + noise * 0.3) * env


class SoundManager:
    """Manages audio playback and WAV file caching."""
    def __init__(self, game):
        self.game = game
        self.enabled = False
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

    def _get_or_create_sound(self, name: str, synth_func) -> pygame.mixer.Sound:
        path = os.path.join(ASSETS_SOUND_DIR, f"{name}.wav")
        if not os.path.exists(path):
            samples = synth_func()
            save_wav(f"{name}.wav", samples)
        return pygame.mixer.Sound(path)

    def _init_sounds(self):
        """Load or synthesize core sound effects."""
        self.sounds["shot"] = self._get_or_create_sound("shotgun_shot", synthesize_shotgun_blast)
        self.sounds["shot"].set_volume(0.85)

        self.sounds["pump"] = self._get_or_create_sound("shotgun_pump", synthesize_shotgun_pump)
        self.sounds["pump"].set_volume(0.7)

        self.sounds["step"] = self._get_or_create_sound("footstep", synthesize_footstep)
        self.sounds["step"].set_volume(0.35)

    def play_shot(self):
        if self.enabled and "shot" in self.sounds:
            self.sounds["shot"].play()

    def play_pump(self):
        if self.enabled and "pump" in self.sounds:
            self.sounds["pump"].play()

    def play_step(self):
        if self.enabled and "step" in self.sounds:
            self.sounds["step"].play()
