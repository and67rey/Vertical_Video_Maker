import pytest
from moviepy.editor import ImageClip
from utils import slide_transition, push_transition
from PIL import Image
import tempfile
import os


@pytest.fixture
def temp_clips():
    """Создаёт два временных ImageClip с разными цветами"""
    clips = []
    for color in ["red", "green"]:
        img = Image.new("RGB", (640, 480), color=color)
        path = tempfile.mktemp(suffix=".png")
        img.save(path)
        clip = ImageClip(path).set_duration(1.0)
        clips.append((clip, path))
    yield [c[0] for c in clips]
    for _, path in clips:
        os.remove(path)


def test_slide_transition_duration(temp_clips):
    """Проверка: slide_transition создаёт клип нужной длительности"""
    transition = slide_transition(temp_clips[0], temp_clips[1], duration=0.5)
    assert transition.duration == 0.5
    assert transition.size == temp_clips[0].size


def test_push_transition_duration(temp_clips):
    """Проверка: push_transition создаёт клип нужной длительности"""
    transition = push_transition(temp_clips[0], temp_clips[1], duration=1.0)
    assert transition.duration == 1.0
    assert transition.size == temp_clips[0].size
