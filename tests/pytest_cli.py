import pytest
from cli import parse_args

@pytest.mark.parametrize("arg_list, expected", [
    (
        ["--images", "images_dir"],
        {"images": "images_dir", "output": "output.mp4", "fps": 24}
    ),
    (
        ["--images", "img", "--audio", "track.mp3", "--duration", "4", "--fps", "30", "--bgcolor", "#FFAA00",
         "--output", "final.mp4", "--bitrate", "5000k", "--crf", "25", "--transition", "slide",
         "--transition-duration", "1", "--mode", "images_loop", "--zoom", "0.2", "--zoom-out", "0.1",
         "--text", "Hello", "--text-position", "top", "--font-size", "42", "--font-color", "white",
         "--font-path", "Arial.ttf", "--logo-path", "logo.png", "--logo-scale", "0.3", "--logo-coords", "100,200",
         "--autocover", "20"],
        {"audio": "track.mp3", "duration": 4.0, "transition": "slide", "mode": "images_loop", "autocover": "20"}
    )
])
def test_parse_args_valid(monkeypatch, arg_list, expected):
    """Проверка корректного разбора аргументов"""
    monkeypatch.setattr("sys.argv", ["prog"] + arg_list)
    args = parse_args()
    for key, val in expected.items():
        assert getattr(args, key) == val


def test_autocover_flag(monkeypatch):
    """Флаг --autocover без значения устанавливает True"""
    monkeypatch.setattr("sys.argv", ["prog", "--images", "img", "--autocover"])
    args = parse_args()
    assert args.autocover is True


def test_invalid_transition(monkeypatch):
    """Недопустимое значение --transition вызывает ошибку"""
    monkeypatch.setattr("sys.argv", ["prog", "--images", "img", "--transition", "flip"])
    with pytest.raises(SystemExit):
        parse_args()


def test_invalid_mode(monkeypatch):
    """Недопустимое значение --mode вызывает ошибку"""
    monkeypatch.setattr("sys.argv", ["prog", "--images", "img", "--mode", "wrongmode"])
    with pytest.raises(SystemExit):
        parse_args()
