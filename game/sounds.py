import pygame
import math
import struct
from io import BytesIO


def generate_sine_wave(frequency, duration, volume=0.3, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    max_amp = int(volume * 32767)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        value = int(max_amp * math.sin(2 * math.pi * frequency * t))
        sample = max(-32768, min(32767, value))
        samples.append(sample)
        samples.append(sample)
    return bytes(struct.pack(f'<{len(samples)}h', *samples))


def generate_wav_bytes(frequency, duration, volume=0.3):
    sample_rate = 44100
    data = generate_sine_wave(frequency, duration, volume, sample_rate)
    n_samples = len(data) // 2
    data_size = len(data)

    buf = BytesIO()
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<I', 16))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<I', sample_rate))
    buf.write(struct.pack('<I', sample_rate * 2))
    buf.write(struct.pack('<H', 2))
    buf.write(struct.pack('<H', 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    buf.write(data)
    buf.seek(0)
    return buf.read()


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_enabled = True
        self.sfx_enabled = True

        self._generate_sounds()
        self._generate_music()

    def _generate_sounds(self):
        eat_freqs = [520, 660, 800]
        eat_dur = 0.08
        eat_samples = []
        sample_rate = 44100
        for i, freq in enumerate(eat_freqs):
            dur = eat_dur * (1 + i * 0.3)
            data = generate_sine_wave(freq, dur, 0.25, sample_rate)
            eat_samples.append(data)
        eat_data = b''.join(eat_samples)
        eat_buf = BytesIO()
        n_samples = len(eat_data) // 2
        eat_buf.write(b'RIFF')
        eat_buf.write(struct.pack('<I', 36 + len(eat_data)))
        eat_buf.write(b'WAVE')
        eat_buf.write(b'fmt ')
        eat_buf.write(struct.pack('<I', 16))
        eat_buf.write(struct.pack('<H', 1))
        eat_buf.write(struct.pack('<H', 1))
        eat_buf.write(struct.pack('<I', sample_rate))
        eat_buf.write(struct.pack('<I', sample_rate * 2))
        eat_buf.write(struct.pack('<H', 2))
        eat_buf.write(struct.pack('<H', 16))
        eat_buf.write(b'data')
        eat_buf.write(struct.pack('<I', len(eat_data)))
        eat_buf.write(eat_data)
        eat_buf.seek(0)
        self.sounds['eat'] = pygame.mixer.Sound(eat_buf)

        game_over_wav = generate_wav_bytes(200, 0.15, 0.3)
        game_over_wav2 = generate_wav_bytes(150, 0.15, 0.3)
        game_over_wav3 = generate_wav_bytes(100, 0.3, 0.3)
        game_over_samples = b''
        sample_rate = 44100
        for wav_data in [game_over_wav, game_over_wav2, game_over_wav3]:
            n = len(wav_data)
            data_start = wav_data.index(b'data') + 8
            game_over_samples += wav_data[data_start:]
        full_buf = BytesIO()
        n_samples = len(game_over_samples) // 2
        full_buf.write(b'RIFF')
        full_buf.write(struct.pack('<I', 36 + len(game_over_samples)))
        full_buf.write(b'WAVE')
        full_buf.write(b'fmt ')
        full_buf.write(struct.pack('<I', 16))
        full_buf.write(struct.pack('<H', 1))
        full_buf.write(struct.pack('<H', 1))
        full_buf.write(struct.pack('<I', sample_rate))
        full_buf.write(struct.pack('<I', sample_rate * 2))
        full_buf.write(struct.pack('<H', 2))
        full_buf.write(struct.pack('<H', 16))
        full_buf.write(b'data')
        full_buf.write(struct.pack('<I', len(game_over_samples)))
        full_buf.write(game_over_samples)
        full_buf.seek(0)
        self.sounds['game_over'] = pygame.mixer.Sound(full_buf)

        click_wav = generate_wav_bytes(880, 0.05, 0.2)
        self.sounds['click'] = pygame.mixer.Sound(BytesIO(click_wav))

    def _generate_music(self):
        sample_rate = 44100
        duration = 4.0
        n_samples = int(sample_rate * duration)
        max_amp = int(0.08 * 32767)
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            value1 = int(max_amp * 0.5 * math.sin(2 * math.pi * 55 * t))
            value2 = int(max_amp * 0.3 * math.sin(2 * math.pi * 110 * t))
            value3 = int(max_amp * 0.2 * math.sin(2 * math.pi * 165 * t))
            value4 = int(max_amp * 0.15 * math.sin(2 * math.pi * 220 * t * (1 + 0.3 * math.sin(2 * math.pi * 0.5 * t))))
            envelope = min(1.0, t * 4, (duration - t) * 4)
            value = int((value1 + value2 + value3 + value4) * envelope)
            sample = max(-32768, min(32767, value))
            samples.append(sample)
            samples.append(sample)

        data = bytes(struct.pack(f'<{len(samples)}h', *samples))
        buf = BytesIO()
        buf.write(b'RIFF')
        buf.write(struct.pack('<I', 36 + len(data)))
        buf.write(b'WAVE')
        buf.write(b'fmt ')
        buf.write(struct.pack('<I', 16))
        buf.write(struct.pack('<H', 1))
        buf.write(struct.pack('<H', 2))
        buf.write(struct.pack('<I', sample_rate))
        buf.write(struct.pack('<I', sample_rate * 4))
        buf.write(struct.pack('<H', 4))
        buf.write(struct.pack('<H', 16))
        buf.write(b'data')
        buf.write(struct.pack('<I', len(data)))
        buf.write(data)
        buf.seek(0)
        self.music_sound = pygame.mixer.Sound(buf)
        self.music_channel = None

    def play_sfx(self, name):
        if self.sfx_enabled and name in self.sounds:
            self.sounds[name].play()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.start_music()
        else:
            self.stop_music()
        return self.music_enabled

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled

    def start_music(self):
        if self.music_enabled and hasattr(self, 'music_sound'):
            self.music_channel = self.music_sound.play(-1)

    def stop_music(self):
        if self.music_channel:
            self.music_channel.stop()
            self.music_channel = None
