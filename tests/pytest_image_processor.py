import os
import tempfile
import pytest
from PIL import Image
from image_processor import load_and_process_images, generate_overlay


@pytest.fixture
def temp_image_dir_with_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        for fmt, color in zip(["JPEG", "PNG", "JPEG"], ["blue", "green", "red"]):
            name = f"test_{color}.{fmt.lower()}"
            Image.new("RGB", (800, 600), color=color).save(os.path.join(temp_dir, name), fmt)

        with open(os.path.join(temp_dir, "broken.png"), "wb") as f:
            f.write(b"not an image")

        with open(os.path.join(temp_dir, "note.txt"), "w") as f:
            f.write("not an image")

        yield temp_dir


@pytest.fixture
def temp_logo_file():
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.new("RGBA", (100, 50), color=(255, 0, 0, 128)).save(path)
    yield path
    os.unlink(path)


def test_load_valid_images_only(temp_image_dir_with_files):
    images = load_and_process_images(temp_image_dir_with_files)
    assert len(images) == 3
    assert all(img.size == (1080, 1920) for img in images)


def test_skip_overlay_behavior(temp_image_dir_with_files, temp_logo_file):
    images = load_and_process_images(temp_image_dir_with_files, text="Overlay", logo_path=temp_logo_file, skip_overlay=True)
    assert len(images) == 3


def test_invalid_color_handling(temp_image_dir_with_files):
    images = load_and_process_images(temp_image_dir_with_files, bgcolor="нецвет")
    assert len(images) == 3


def test_invalid_logo_path(temp_image_dir_with_files):
    images = load_and_process_images(temp_image_dir_with_files, logo_path="missing_logo.png")
    assert len(images) == 3


def test_invalid_logo_coords(temp_image_dir_with_files, temp_logo_file):
    images = load_and_process_images(temp_image_dir_with_files, logo_path=temp_logo_file, logo_coords="abc,xyz")
    assert len(images) == 3


def test_invalid_font_and_text(temp_image_dir_with_files):
    images = load_and_process_images(temp_image_dir_with_files, text="Текст", font_path="missing_font.ttf", font_color="no_color", text_position="top")
    assert len(images) == 3


def test_generate_overlay_with_text_and_logo(temp_logo_file):
    overlay = generate_overlay(
        text="Overlay Test",
        text_position="center",
        font_size=40,
        font_color="white",
        logo_path=temp_logo_file,
        logo_scale=0.1,
        logo_coords="20,30"
    )
    assert isinstance(overlay, Image.Image)
    assert overlay.size == (1080, 1920)


def test_generate_overlay_text_only():
    overlay = generate_overlay(text="Just text")
    assert isinstance(overlay, Image.Image)


def test_generate_overlay_with_invalid_data():
    overlay = generate_overlay(
        text="Faulty",
        font_path="missing_font.ttf",
        font_color="badcolor",
        logo_path="missing_logo.png",
        logo_coords="not,coords"
    )
    assert isinstance(overlay, Image.Image)


def test_text_draw_failure(monkeypatch, temp_image_dir_with_files):
    # Подменим метод textbbox на выброс исключения
    from PIL import ImageDraw

    original_textbbox = ImageDraw.ImageDraw.textbbox

    def broken_textbbox(self, *args, **kwargs):
        raise ValueError("textbbox failed")

    monkeypatch.setattr(ImageDraw.ImageDraw, "textbbox", broken_textbbox)

    images = load_and_process_images(temp_image_dir_with_files, text="Ошибка текста")
    assert len(images) == 3

    # Восстановим метод (для безопасности в изолированной сессии)
    monkeypatch.setattr(ImageDraw.ImageDraw, "textbbox", original_textbbox)


def test_valid_logo_coords_as_string(temp_image_dir_with_files, temp_logo_file):
    images = load_and_process_images(
        temp_image_dir_with_files,
        logo_path=temp_logo_file,
        logo_coords="10,20"
    )
    assert len(images) == 3


def test_generate_overlay_valid_coords():
    overlay = generate_overlay(
        text="Проверка",
        logo_path=None,
        logo_coords="100,200"
    )
    assert isinstance(overlay, Image.Image)


def test_image_processing_with_invalid_color_and_logo_coords():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Подкаталог для изображений
        img_dir = os.path.join(tmpdir, "imgs")
        os.makedirs(img_dir)
        img_path = os.path.join(img_dir, "test.jpg")
        Image.new("RGB", (500, 500), "blue").save(img_path)

        # Логотип — в отдельной папке
        logo_path = os.path.join(tmpdir, "logo.png")
        Image.new("RGBA", (100, 100), (255, 0, 0, 128)).save(logo_path)

        images = load_and_process_images(
            directory=img_dir,
            bgcolor="invalid_color",
            text="Тест",
            text_position="center",
            font_size=20,
            font_color="green",
            font_path="/invalid/font/path.ttf",
            logo_path=logo_path,
            logo_scale=0.1,
            logo_coords="100,200",
            skip_overlay=False
        )

        assert len(images) == 1


def test_generate_overlay_full_branch():
    with tempfile.TemporaryDirectory() as tmpdir:
        logo_path = os.path.join(tmpdir, "logo.png")
        Image.new("RGBA", (100, 100), (255, 255, 0, 128)).save(logo_path)

        overlay = generate_overlay(
            text="Overlay",
            text_position="top",
            font_size=24,
            font_color="blue",
            font_path="/nonexistent/path.ttf",
            logo_path=logo_path,
            logo_scale=0.05,
            logo_coords=[10, 10]
        )

        assert overlay is not None


def test_invalid_font_path(monkeypatch, tmp_path):
    # Создаём временное изображение
    img_path = tmp_path / "test.jpg"
    Image.new("RGB", (100, 100)).save(img_path)

    # Переопределяем путь к шрифту на несуществующий
    invalid_font_path = "/nonexistent/font.ttf"

    # Вызываем функцию с некорректным шрифтом
    images = load_and_process_images(
        directory=tmp_path,
        text="Тест",
        font_path=invalid_font_path
    )

    # Проверяем, что изображение обработано
    assert len(images) == 1


def test_invalid_logo_coords(monkeypatch, tmp_path):
    # Создаём временное изображение
    img_path = tmp_path / "test.jpg"
    Image.new("RGB", (100, 100)).save(img_path)

    # Создаём временный логотип
    logo_path = tmp_path / "logo.png"
    Image.new("RGBA", (50, 50)).save(logo_path)

    # Передаём некорректные координаты
    invalid_coords = "invalid,coords"

    # Вызываем функцию с некорректными координатами
    images = load_and_process_images(
        directory=tmp_path,
        logo_path=logo_path,
        logo_coords="invalid,coords"
    )
    assert len(images) == 2


def test_generate_overlay_invalid_logo_coords(monkeypatch, tmp_path):
    # Создаём временный логотип
    logo_path = tmp_path / "logo.png"
    Image.new("RGBA", (50, 50)).save(logo_path)

    # Передаём некорректные координаты
    invalid_coords = "invalid,coords"

    # Вызываем функцию с некорректными координатами
    overlay = generate_overlay(
        text="Тест",
        logo_path=logo_path,
        logo_coords=invalid_coords
    )

    # Проверяем, что оверлей создан
    assert overlay is not None
