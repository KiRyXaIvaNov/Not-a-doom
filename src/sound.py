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
    noise = np.random.uniform(-0.15, 0.15, total_samples)
    env = np.exp(-t * 60)
    return noise * env * 0.35


def synthesize_demon_pain() -> np.ndarray:
    """Demonic guttural grunt/snarl when taking damage."""
    duration = 0.32
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    f_mod = 125 * np.exp(-t * 6) + 50
    mod = np.sin(2 * np.pi * 35 * t)
    carrier = np.sin(2 * np.pi * (f_mod + 30 * mod) * t)
    noise = np.random.uniform(-0.4, 0.4, total_samples) * np.exp(-t * 5)
    env = np.exp(-t * 7)
    env[:int(0.01 * SAMPLE_RATE)] = np.linspace(0, 1, int(0.01 * SAMPLE_RATE))
    raw = (carrier * 0.7 + noise * 0.5) * env
    return np.tanh(raw * 2.2)


def synthesize_demon_death() -> np.ndarray:
    """Demonic screech descending into an explosive death rupture."""
    duration = 0.75
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    f_mod = 420 * np.exp(-t * 4.5) + 60
    lfo = np.sin(2 * np.pi * 28 * t)
    tone = np.sin(2 * np.pi * (f_mod + 45 * lfo) * t)
    noise = np.random.uniform(-0.8, 0.8, total_samples)
    env = np.exp(-t * 3.8)
    env[:int(0.02 * SAMPLE_RATE)] = np.linspace(0, 1, int(0.02 * SAMPLE_RATE))
    boom = np.sin(2 * np.pi * 70 * np.exp(-t * 8) * t) * 0.6
    raw = (tone * 0.5 + noise * 0.6 + boom) * env
    return np.tanh(raw * 2.5)


def synthesize_demon_alert() -> np.ndarray:
    """Rising demonic hiss/roar when spotting or pursuing player."""
    duration = 0.42
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    f_mod = 180 + 160 * np.sin(np.pi * t / duration)
    mod = np.sin(2 * np.pi * 45 * t)
    carrier = np.sin(2 * np.pi * (f_mod + 40 * mod) * t)
    noise = np.random.uniform(-0.6, 0.6, total_samples)
    env = np.sin(np.pi * t / duration) ** 0.8
    raw = (carrier * 0.6 + noise * 0.5) * env
    return np.tanh(raw * 2.4)


def synthesize_player_hurt() -> np.ndarray:
    """Classic low player pain grunt/thud upon receiving damage."""
    duration = 0.26
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    f_mod = 140 * np.exp(-t * 10) + 75
    tone = np.sin(2 * np.pi * f_mod * t)
    noise = np.random.uniform(-0.3, 0.3, total_samples) * np.exp(-t * 12)
    env = np.exp(-t * 9)
    env[:int(0.008 * SAMPLE_RATE)] = np.linspace(0.1, 1.0, int(0.008 * SAMPLE_RATE))
    raw = (tone * 0.75 + noise * 0.35) * env
    return np.tanh(raw * 2.0)


def synthesize_fireball_launch() -> np.ndarray:
    """Fiery whoosh of demon plasma ball ignition."""
    duration = 0.35
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    noise = np.random.uniform(-0.8, 0.8, total_samples)
    freq = 240 * np.exp(-t * 8) + 80
    whoosh = np.sin(2 * np.pi * freq * t)
    env = np.sin(np.pi * t / duration) ** 0.9
    raw = (whoosh * 0.5 + noise * 0.5) * env
    return np.tanh(raw * 2.2)


def synthesize_medkit_pickup() -> np.ndarray:
    """Bright positive retro healing pickup sound (two-tone arpeggio)."""
    duration = 0.28
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    freq = np.where(t < 0.10, 523.25, 783.99)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    tone = np.sin(phase) + 0.35 * np.sin(2 * phase)
    env = np.exp(-t * 8.0)
    env[:int(0.01 * SAMPLE_RATE)] = np.linspace(0, 1, int(0.01 * SAMPLE_RATE))
    raw = tone * env * 0.4
    return np.clip(raw, -1.0, 1.0)


def synthesize_teleport_win() -> np.ndarray:
    """Victorious ascending harmonic teleporter chime."""
    duration = 0.8
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    chord1 = np.sin(2 * np.pi * 440 * t)
    chord2 = np.sin(2 * np.pi * 554.37 * t)
    chord3 = np.sin(2 * np.pi * 659.25 * t)
    chord4 = np.sin(2 * np.pi * 880 * t)
    shimmer = 1.0 + 0.3 * np.sin(2 * np.pi * 16 * t)
    env = np.exp(-t * 2.5)
    env[:int(0.02 * SAMPLE_RATE)] = np.linspace(0, 1, int(0.02 * SAMPLE_RATE))
    raw = (chord1 * 0.25 + chord2 * 0.25 + chord3 * 0.3 + chord4 * 0.35) * shimmer * env
    return np.tanh(raw * 1.5)


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
        step_file = self._find_audio_file("footstep")
        if not step_file:
            step_file = save_wav("footstep.wav", synthesize_footstep())
        self.sounds["step"] = pygame.mixer.Sound(step_file)
        self.sounds["step"].set_volume(0.10)  # Soft background volume

        # 4. Demonic combat sounds (tuned comfortable volume, ~40% quieter)
        pain_file = self._find_audio_file("demon_pain")
        if not pain_file:
            pain_file = save_wav("demon_pain.wav", synthesize_demon_pain())
        self.sounds["demon_pain"] = pygame.mixer.Sound(pain_file)
        self.sounds["demon_pain"].set_volume(0.10)

        death_file = self._find_audio_file("demon_death")
        if not death_file:
            death_file = save_wav("demon_death.wav", synthesize_demon_death())
        self.sounds["demon_death"] = pygame.mixer.Sound(death_file)
        self.sounds["demon_death"].set_volume(0.15)

        alert_file = self._find_audio_file("demon_alert")
        if not alert_file:
            alert_file = save_wav("demon_alert.wav", synthesize_demon_alert())
        self.sounds["demon_alert"] = pygame.mixer.Sound(alert_file)
        self.sounds["demon_alert"].set_volume(0.10)

        # 5. Player hurt sound
        hurt_file = self._find_audio_file("player_hurt")
        if not hurt_file:
            hurt_file = save_wav("player_hurt.wav", synthesize_player_hurt())
        self.sounds["player_hurt"] = pygame.mixer.Sound(hurt_file)
        self.sounds["player_hurt"].set_volume(0.75)

        # 6. Demonic fireball launch sound
        fireball_file = self._find_audio_file("fireball_launch")
        if not fireball_file:
            fireball_file = save_wav("fireball_launch.wav", synthesize_fireball_launch())
        self.sounds["fireball_launch"] = pygame.mixer.Sound(fireball_file)
        self.sounds["fireball_launch"].set_volume(0.20)

        # 7. Teleport level complete sound
        teleport_file = self._find_audio_file("teleport_win")
        if not teleport_file:
            teleport_file = save_wav("teleport_win.wav", synthesize_teleport_win())
        self.sounds["teleport_win"] = pygame.mixer.Sound(teleport_file)
        self.sounds["teleport_win"].set_volume(0.40)

        # 8. Medkit health pickup sound
        medkit_file = self._find_audio_file("medkit")
        if not medkit_file:
            medkit_file = save_wav("medkit.wav", synthesize_medkit_pickup())
        self.sounds["medkit"] = pygame.mixer.Sound(medkit_file)
        self.sounds["medkit"].set_volume(0.35)

    def play_shot(self):
        if self.enabled and "shot" in self.sounds:
            self.sounds["shot"].play()

    def play_pump(self):
        if self.enabled and not self.has_integrated_pump and "pump" in self.sounds:
            self.sounds["pump"].play()

    def play_step(self):
        if self.enabled and "step" in self.sounds:
            self.sounds["step"].play()

    def play_demon_pain(self):
        if self.enabled and "demon_pain" in self.sounds:
            self.sounds["demon_pain"].play()

    def play_demon_death(self):
        if self.enabled and "demon_death" in self.sounds:
            self.sounds["demon_death"].play()

    def play_demon_alert(self):
        if self.enabled and "demon_alert" in self.sounds:
            self.sounds["demon_alert"].play()

    def play_player_hurt(self):
        if self.enabled and "player_hurt" in self.sounds:
            self.sounds["player_hurt"].play()

    def play_fireball_launch(self):
        if self.enabled and "fireball_launch" in self.sounds:
            self.sounds["fireball_launch"].play()

    def play_teleport_win(self):
        if self.enabled and "teleport_win" in self.sounds:
            self.sounds["teleport_win"].play()

    def play_medkit(self):
        if self.enabled and "medkit" in self.sounds:
            self.sounds["medkit"].play()
