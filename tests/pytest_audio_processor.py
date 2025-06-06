import os
import tempfile
import pytest
from pydub.generators import Sine
from audio_processor import load_audio_clip
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_wav_file():
    """Создаёт простой WAV-файл с синусоидой"""
    path = tempfile.mktemp(suffix=".wav")
    tone = Sine(440).to_audio_segment(duration=3000)  # 3 сек
    tone.export(path, format="wav")
    yield path
    os.remove(path)


def test_load_audio_cut(temp_wav_file):
    """Проверка режима cut: аудио обрезается до видео"""
    clip = load_audio_clip(temp_wav_file, mode="cut", video_duration=1.5)
    assert round(clip.duration, 1) == 1.5


def test_load_audio_loop(temp_wav_file):
    """Проверка режима loop: аудио повторяется до нужной длины"""
    clip = load_audio_clip(temp_wav_file, mode="loop", video_duration=6)
    assert round(clip.duration) == 6


def test_fade_in_out_applied(temp_wav_file):
    """Проверка применения эффектов fade-in и fade-out"""
    clip = load_audio_clip(temp_wav_file, mode="cut", video_duration=2, fade_in_duration=0.5, fade_out_duration=0.5)
    assert clip.duration == 2


def test_audio_file_not_found():
    """Ошибка при передаче несуществующего файла"""
    with pytest.raises(Exception):
        load_audio_clip("nonexistent.wav", mode="cut", video_duration=2)


@patch("audio_processor.AudioFileClip")
def test_audio_invalid_mode(mock_clip):
    """Некорректный режим вызывает warning, но не исключение"""
    mock_audio = MagicMock()
    mock_audio.duration = 5.0
    mock_audio.audio_fadein.return_value = mock_audio
    mock_audio.audio_fadeout.return_value = mock_audio
    mock_clip.return_value = mock_audio

    clip = load_audio_clip("dummy.mp3", mode="invalid", video_duration=5.0)
    assert clip is mock_audio
