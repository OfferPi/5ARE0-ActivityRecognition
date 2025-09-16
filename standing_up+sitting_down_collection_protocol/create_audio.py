#!/usr/bin/env python3
import os
import wave
import math
import struct
import tempfile
import subprocess
from typing import Tuple

import numpy as np

# ------------------ Config ------------------
SAMPLE_RATE = 22050  # espeak-ng defaults to 22050Hz; keep this to avoid resampling
BIT_DEPTH = 16       # 16-bit PCM
CHANNELS = 1

TOTAL_DURATION_S = 625.0

COUNTDOWN_START_S = 13.0  # 13 → "3", 14 → "2", 15 → "1"
TONE_FIRST_TIME_S = 15
TONE_INTERVAL_S = 5.0
TONE_DURATION_S = 0.5     # seconds

FREQ_HIGH = 1000.0
FREQ_LOW  = 400.0

# Gains (linear multipliers; keep below 1.0 to avoid clipping)
TONE_GAIN = 0.5
SPEECH_GAIN = 0.9

WELCOME_TEXT = "Welcome, we will start in a few seconds. Start this research by standing up right, when you hear a high tone sit down, when you hear a low tone stand up again. Do this until you get instructed to stop"
FINAL_TEXT   = "thanks your done, you can stop!" 

# -------------------------------------------

def synth_sine(freq_hz: float, duration_s: float, sr: int, fade_ms: int = 10) -> np.ndarray:
    """Generate a mono sine wave float32 in [-1, 1] with short fade in/out."""
    n = int(sr * duration_s)
    t = np.arange(n) / sr
    wave = np.sin(2.0 * np.pi * freq_hz * t).astype(np.float32)

    # fade
    fade_len = int(sr * (fade_ms / 1000.0))
    if fade_len > 0 and fade_len < n // 2:
        fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        wave[:fade_len] *= fade_in
        wave[-fade_len:] *= fade_out
    return wave

def write_wav(path: str, data_float_mono: np.ndarray, sr: int = SAMPLE_RATE) -> None:
    """Write float32 mono [-1,1] to 16-bit PCM WAV."""
    # clip and convert
    data_clipped = np.clip(data_float_mono, -1.0, 1.0)
    data_int16 = (data_clipped * 32767.0).astype(np.int16)

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sr)
        wf.writeframes(data_int16.tobytes())

def read_wav_as_float_mono(path: str) -> Tuple[np.ndarray, int]:
    """Read WAV (any mono/stereo, any sr) → float32 mono [-1,1], return (audio, sr)."""
    with wave.open(path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)

    # Decode PCM
    if sampwidth == 2:
        dtype = np.int16
        scale = 32768.0
    elif sampwidth == 1:
        dtype = np.uint8  # unsigned
        scale = 128.0
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth*8} bits")

    audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)

    if sampwidth == 1:
        # Convert unsigned 8-bit to centered float
        audio = (audio - 128.0) / 128.0
    else:
        audio = audio / 32768.0

    # Handle channels: average to mono if stereo
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    elif n_channels != 1:
        raise ValueError(f"Unsupported channels: {n_channels}")

    return audio, framerate

def resample_linear(x: np.ndarray, sr_from: int, sr_to: int) -> np.ndarray:
    """Simple linear resample (good enough for TTS snippets)."""
    if sr_from == sr_to:
        return x
    duration = len(x) / sr_from
    n_to = int(round(duration * sr_to))
    if n_to <= 1:
        return np.zeros((n_to,), dtype=np.float32)
    t_from = np.linspace(0.0, duration, num=len(x), endpoint=False)
    t_to = np.linspace(0.0, duration, num=n_to, endpoint=False)
    return np.interp(t_to, t_from, x).astype(np.float32)

def espeak_to_wav(text: str, voice: str = "en", speed_wpm: int = 150) -> np.ndarray:
    """Call espeak-ng to synthesize text to wav → return float32 mono at SAMPLE_RATE."""
    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "tts.wav")
        cmd = ["espeak-ng", "-v", voice, "-s", str(speed_wpm), "-w", out_path, text]
        subprocess.run(cmd, check=True)
        audio, sr = read_wav_as_float_mono(out_path)
    audio = resample_linear(audio, sr, SAMPLE_RATE)
    return audio

def mix_at(timeline: np.ndarray, clip: np.ndarray, at_seconds: float, gain: float = 1.0) -> None:
    """Mix clip (float32) into timeline in-place at given time with gain."""
    start = int(round(at_seconds * SAMPLE_RATE))
    end = start + len(clip)
    if start >= len(timeline):
        return
    end = min(end, len(timeline))
    sl = end - start
    if sl > 0:
        timeline[start:end] += gain * clip[:sl]

def main():
    n_total = int(TOTAL_DURATION_S * SAMPLE_RATE) + 1
    timeline = np.zeros((n_total,), dtype=np.float32)

    # --- Speech ---
    welcome = espeak_to_wav(WELCOME_TEXT, voice="en", speed_wpm=150)
    three   = espeak_to_wav("3", voice="en", speed_wpm=150)
    two     = espeak_to_wav("2", voice="en", speed_wpm=150)
    one     = espeak_to_wav("1", voice="en", speed_wpm=150)
    final   = espeak_to_wav(FINAL_TEXT, voice="en", speed_wpm=150)

    mix_at(timeline, welcome, 0.0, SPEECH_GAIN)
    mix_at(timeline, three,   COUNTDOWN_START_S + 0.0, SPEECH_GAIN)  # 13
    mix_at(timeline, two,     COUNTDOWN_START_S + 1.0, SPEECH_GAIN)  # 14
    mix_at(timeline, one,     COUNTDOWN_START_S + 2.0, SPEECH_GAIN)  # 15
    mix_at(timeline, final,   TOTAL_DURATION_S,        SPEECH_GAIN)  # 325

    # --- Tones ---
    tone_high = synth_sine(FREQ_HIGH, TONE_DURATION_S, SAMPLE_RATE) * TONE_GAIN
    tone_low  = synth_sine(FREQ_LOW,  TONE_DURATION_S, SAMPLE_RATE) * TONE_GAIN

    t = TONE_FIRST_TIME_S
    use_high = True
    while t <= TOTAL_DURATION_S:
        mix_at(timeline, tone_high if use_high else tone_low, t, 1.0)
        t += TONE_INTERVAL_S
        use_high = not use_high

    # Soft limiter to avoid clipping if speech + tone overlap
    peak = np.max(np.abs(timeline))
    if peak > 0.99:
        timeline /= peak / 0.98

    write_wav("protocol.wav", timeline, SAMPLE_RATE)
    print("✅ Created protocol.wav")

if __name__ == "__main__":
    main()
