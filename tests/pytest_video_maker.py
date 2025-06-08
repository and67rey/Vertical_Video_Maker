import os
import tempfile
import pytest
from PIL import Image
from video_maker import create_video_from_images
from image_processor import generate_overlay
from pydub.generators import Sine
from moviepy.editor import AudioFileClip, VideoFileClip, AudioClip
from moviepy.audio.AudioClip import AudioClip


@pytest.fixture
def temp_images():
    return [Image.new("RGB", (1080, 1920), color=c) for c in ["red", "green", "blue"]]


@pytest.fixture
def temp_overlay():
    return [generate_overlay(text="Overlay", text_position="top") for _ in range(3)]


@pytest.fixture
def temp_audio_file():
    path = tempfile.mktemp(suffix=".wav")
    tone = Sine(440).to_audio_segment(duration=5000)
    tone.export(path, format="wav")
    yield path
    os.remove(path)


@pytest.mark.parametrize("transition", ["none", "fade", "slide", "push"])
def test_create_video_with_transitions(temp_images, transition):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition=transition,
        transition_duration=0.5,
        bitrate="800k",
        crf=None,
        audio_clip=None,
        zoom_factor=0.1,
        zoom_out_factor=0.0
    )

    assert os.path.exists(output_path) and os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_video_with_zoom_out(temp_images):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="fade",
        transition_duration=0.5,
        bitrate="500k",
        crf=23,
        audio_clip=None,
        zoom_factor=0.0,
        zoom_out_factor=0.1
    )

    assert os.path.exists(output_path) and os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_video_with_audio(temp_images, temp_audio_file):
    audio_clip = AudioFileClip(temp_audio_file)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="none",
        transition_duration=0.5,
        bitrate="1000k",
        crf=None,
        audio_clip=audio_clip,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )

    audio_clip.close()
    assert os.path.exists(output_path) and os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_video_duration_matches_audio(temp_images, temp_audio_file):
    audio_clip = AudioFileClip(temp_audio_file)
    expected_duration = round(audio_clip.duration, 1)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="fade",
        transition_duration=0.5,
        bitrate="500k",
        crf=None,
        audio_clip=audio_clip,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )
    audio_clip.close()

    with VideoFileClip(output_path) as video:
        video_duration = round(video.duration, 1)

    os.remove(output_path)
    assert expected_duration == video_duration


def test_audio_loop_exact_match(temp_images):
    audio_clip = AudioClip(lambda t: [0], duration=3.0)
    audio_clip.fps = 44100

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="none",
        transition_duration=0.5,
        bitrate="1000k",
        crf=None,
        audio_clip=audio_clip,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )

    assert os.path.exists(output_path) and os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_video_with_overlay(temp_images, temp_overlay):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.5,
        fps=24,
        output_path=output_path,
        transition="fade",
        transition_duration=0.5,
        bitrate="800k",
        crf=None,
        audio_clip=None,
        zoom_factor=0.1,
        zoom_out_factor=0.0,
        overlays=temp_overlay
    )

    assert os.path.exists(output_path) and os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_create_video_with_empty_images_list(caplog, tmp_path):
    """Проверка обработки пустого списка изображений (safe return)"""
    output = tmp_path / "empty.mp4"

    with caplog.at_level("ERROR"):
        create_video_from_images(
            images=[],
            duration=1.0,
            fps=24,
            output_path=str(output),
            transition="none"
        )

    assert "Список изображений пуст." in caplog.text


def test_create_video_with_push_transition(temp_images):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="push",
        transition_duration=0.5,
        bitrate="800k",
        crf=None,
        audio_clip=None,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    os.remove(output_path)


def test_audio_loop_exact_match_branch(temp_images):
    from moviepy.audio.AudioClip import AudioClip

    # 3 изображения по 1с = 3с
    audio_clip = AudioClip(lambda t: [0], duration=3.0)
    audio_clip.fps = 44100

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="none",
        transition_duration=0.5,
        bitrate="1000k",
        crf=None,
        audio_clip=audio_clip,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )

    assert os.path.exists(output_path)
    os.remove(output_path)

def test_video_export_with_crf(temp_images):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    create_video_from_images(
        images=temp_images,
        duration=1.0,
        fps=24,
        output_path=output_path,
        transition="none",
        transition_duration=0.5,
        bitrate="500k",  # должен быть проигнорирован
        crf=23,
        audio_clip=None,
        zoom_factor=0.0,
        zoom_out_factor=0.0
    )

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    os.remove(output_path)

