import pytest
import os
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from runner import run_vvm


@pytest.fixture
def minimal_args(tmp_path):
    return SimpleNamespace(
        images=str(tmp_path),
        bgcolor="black",
        text=None,
        text_position="bottom",
        font_size=40,
        font_color="white",
        font_path=None,
        logo_path=None,
        logo_scale=0.1,
        logo_coords=None,
        autocover=None,
        duration=1.0,
        fps=24,
        output="dummy.mp4",
        bitrate="1000k",
        crf=None,
        audio=None,
        transition="none",
        transition_duration=0.5,
        zoom=0.0,
        zoom_out=0.0,
        mode="basic"
    )


@patch("runner.create_video_from_images")
@patch("runner.load_audio_clip")
@patch("runner.load_and_process_images")
@patch("runner.AudioFileClip")
def test_run_vvm_minimal(mock_audiofile, mock_load_images, mock_load_audio, mock_create_video, minimal_args):
    mock_img = MagicMock()
    mock_img.save = MagicMock()
    mock_load_images.return_value = [mock_img] * 3

    run_vvm(minimal_args)

    mock_load_images.assert_called_once()
    mock_create_video.assert_called_once()
    assert mock_create_video.call_args[1]["images"] == [mock_img] * 3
    assert mock_create_video.call_args[1]["overlays"] is None


@patch("runner.generate_overlay", return_value="dummy_overlay")
@patch("runner.create_video_from_images")
@patch("runner.load_audio_clip")
@patch("runner.load_and_process_images")
@patch("runner.AudioFileClip")
def test_run_vvm_zoom_overlay_generation(mock_audiofile, mock_load_images, mock_load_audio, mock_create_video, mock_overlay, minimal_args):
    minimal_args.zoom = 0.2  # Активирует skip_overlay
    minimal_args.text = "Overlayed"
    mock_img = MagicMock()
    mock_img.save = MagicMock()
    mock_load_images.return_value = [mock_img] * 2

    run_vvm(minimal_args)

    mock_overlay.assert_called_once()
    assert mock_create_video.call_args[1]["overlays"] == ["dummy_overlay"] * 2


@patch("runner.create_video_from_images")
@patch("runner.load_audio_clip")
@patch("runner.load_and_process_images")
@patch("runner.AudioFileClip")
def test_run_vvm_autocover_frame(mock_audiofile, mock_load_images, mock_load_audio, mock_create_video, minimal_args):
    minimal_args.autocover = True
    mock_img = MagicMock()
    mock_img.save = MagicMock()
    mock_load_images.return_value = [mock_img] * 4

    run_vvm(minimal_args)
    mock_img.save.assert_called_once_with("thumbnail.png")


@patch("runner.create_video_from_images")
@patch("runner.load_and_process_images", return_value=[])
def test_run_vvm_empty_images(mock_load_images, mock_create_video, minimal_args):
    run_vvm(minimal_args)
    mock_create_video.assert_not_called()


@patch("runner.AudioFileClip", side_effect=Exception("Broken audio"))
@patch("runner.load_and_process_images", return_value=[MagicMock(save=MagicMock())])
@patch("runner.create_video_from_images")
def test_run_vvm_audiofile_exception(mock_create_video, mock_load_images, mock_audiofile, minimal_args):
    minimal_args.audio = "bad.mp3"
    run_vvm(minimal_args)
    mock_create_video.assert_called_once()


@patch("runner.load_audio_clip", side_effect=Exception("Decoder error"))
@patch("runner.AudioFileClip", return_value=MagicMock(duration=10.0))
@patch("runner.load_and_process_images", return_value=[MagicMock(save=MagicMock())])
@patch("runner.create_video_from_images")
def test_run_vvm_audio_clip_exception(mock_create_video, mock_load_images, mock_audiofile, mock_load_audio, minimal_args):
    minimal_args.audio = "broken.mp3"
    run_vvm(minimal_args)
    mock_load_audio.assert_called_once()
    mock_create_video.assert_called_once()


@patch("runner.create_video_from_images")
@patch("runner.load_audio_clip")
@patch("runner.load_and_process_images")
@patch("runner.AudioFileClip")
def test_run_vvm_images_loop_mode(mock_audiofile, mock_load_images, mock_load_audio, mock_create_video, minimal_args):
    minimal_args.mode = "images_loop"
    minimal_args.audio = "short.mp3"
    mock_audiofile.return_value.duration = 1.0
    mock_load_images.return_value = [MagicMock(save=MagicMock())] * 4

    run_vvm(minimal_args)
    mock_create_video.assert_called_once()
    assert mock_create_video.call_args[1]["duration"] == minimal_args.duration


@patch("runner.create_video_from_images")
@patch("runner.load_audio_clip")
@patch("runner.load_and_process_images")
@patch("runner.AudioFileClip")
def test_run_vvm_autocover_by_second(mock_audiofile, mock_load_images, mock_load_audio, mock_create_video, minimal_args):
    minimal_args.autocover = "1.0"
    minimal_args.duration = 2.0
    mock_img = MagicMock()
    mock_img.save = MagicMock()
    mock_load_images.return_value = [mock_img] * 3

    run_vvm(minimal_args)
    mock_img.save.assert_called_once_with("thumbnail.png")


@patch("runner.load_and_process_images", return_value=[])
@patch("runner.create_video_from_images")
def test_run_vvm_no_images_loaded(mock_create_video, mock_load_images, minimal_args, caplog):
    """Проверка обработки случая, когда изображения не загружены"""
    with caplog.at_level("ERROR"):
        run_vvm(minimal_args)

    assert "Не удалось загрузить изображения." in caplog.text
    mock_create_video.assert_not_called()


@patch("runner.load_and_process_images", return_value=[])
@patch("runner.create_video_from_images")
def test_run_vvm_autocover_no_images(mock_create_video, mock_load_images, minimal_args, caplog):
    """Обработка autocover при отсутствии изображений"""
    minimal_args.autocover = "3"
    minimal_args.audio = None  # отключаем аудио, чтобы не мешало

    with caplog.at_level("ERROR"):
        run_vvm(minimal_args)

    assert "Не удалось загрузить изображения" in caplog.text
    assert not mock_create_video.called  # видео не создаётся, если нет изображений


@patch("runner.load_and_process_images", return_value=[MagicMock(save=MagicMock())])
@patch("runner.create_video_from_images")
def test_invalid_output_extension_replaced(mock_create_video, mock_load_images, minimal_args):
    minimal_args.output = "video.invalid"
    run_vvm(minimal_args)
    assert minimal_args.output.endswith(".mp4")
    mock_create_video.assert_called_once()


@patch("runner.load_and_process_images", return_value=[MagicMock(save=MagicMock())])
@patch("runner.create_video_from_images")
def test_output_as_directory(mock_create_video, mock_load_images, tmp_path, minimal_args):
    dir_path = tmp_path / "new_output"
    minimal_args.output = str(dir_path)
    run_vvm(minimal_args)
    assert os.path.exists(dir_path)
    assert minimal_args.output.endswith("output.mp4")
    mock_create_video.assert_called_once()


@patch("runner.load_and_process_images", return_value=[MagicMock(save=MagicMock())])
@patch("runner.create_video_from_images")
def test_create_output_directory(mock_create_video, mock_load_images, tmp_path, minimal_args):
    output_file = tmp_path / "new_dir" / "video.mp4"
    minimal_args.output = str(output_file)
    run_vvm(minimal_args)
    assert os.path.exists(output_file.parent)
    mock_create_video.assert_called_once()


@patch("runner.load_and_process_images")
@patch("runner.create_video_from_images")
def test_autocover_custom_output(mock_create_video, mock_load_images, tmp_path, minimal_args):
    minimal_args.autocover = True
    img_mock = MagicMock()
    img_mock.save = MagicMock()
    mock_dir = tmp_path / "out"
    mock_dir.mkdir()
    minimal_args.output = str(mock_dir / "custom.mp4")
    mock_load_images.return_value = [img_mock]
    run_vvm(minimal_args)
    img_mock.save.assert_called_once_with(os.path.join(str(mock_dir), "thumbnail.png"))


@patch("runner.load_and_process_images")
@patch("runner.create_video_from_images")
def test_autocover_zero_second(mock_create_video, mock_load_images, minimal_args):
    minimal_args.autocover = "0"
    minimal_args.duration = 2.0
    img_mock = MagicMock()
    img_mock.save = MagicMock()
    mock_load_images.return_value = [img_mock] * 5
    run_vvm(minimal_args)
    img_mock.save.assert_called_once()
