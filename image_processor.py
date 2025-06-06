# image_processor.py
import os
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageColor
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

# Целевой размер выходного изображения (видео формат 9:16)
TARGET_SIZE = (1080, 1920)

def load_and_process_images(directory, bgcolor="black", text=None, text_position="bottom",
                            font_size=40, font_color="white", font_path=None,
                            logo_path=None, logo_scale=0.2, logo_coords=None,
                            skip_overlay=False):
    """
    Загружает изображения из указанного каталога, подгоняет их под нужный размер,
    наносит текст и логотип (если не активен skip_overlay).
    """

    # Преобразуем цвет фона в RGB. Если указан неверно — используем чёрный.
    try:
        color = ImageColor.getrgb(bgcolor)
    except ValueError:
        logger.warning("Неверный цвет '%s', используется по умолчанию — 'black'", bgcolor)
        color = (0, 0, 0)

    images = []

    # Перебираем все файлы в каталоге
    for filename in tqdm(sorted(os.listdir(directory))):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(directory, filename)
            try:
                # Загружаем изображение и адаптируем под целевой размер (с фоном)
                img = Image.open(path).convert("RGB")
                img = ImageOps.pad(img, (1080, 1920), method=Image.Resampling.LANCZOS, color=color)

                # Добавляем текст, если задан и overlay не отключён
                if text and not skip_overlay:
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype(font_path if font_path else "arial.ttf", font_size)
                    except Exception as e:
                        font = ImageFont.load_default()
                        logger.warning("Шрифт по пути '%s' не найден. Используется шрифт по умолчанию. Ошибка: %s", font_path, e)

                    try:
                        # Вычисляем размеры текста и размещаем его в нужной позиции
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]

                        if text_position == "top":
                            position = ((img.width - text_width) // 2, 50)
                        elif text_position == "center":
                            position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
                        else:  # default: bottom
                            position = ((img.width - text_width) // 2, img.height - text_height - 50)

                        draw.text(position, text, fill=font_color, font=font)
                        logger.info("Добавлен текст: '%s' на позицию %s", text, text_position)
                    except Exception as e:
                        logger.warning("Не удалось отрисовать текст '%s': %s", text, e)

                # Добавляем логотип, если указан и overlay не отключён
                if logo_path and not skip_overlay:
                    try:
                        logo = Image.open(logo_path).convert("RGBA")

                        # Масштабируем логотип пропорционально ширине изображения
                        logo_width = int(img.width * logo_scale)
                        logo_ratio = logo_width / logo.width
                        logo_height = int(logo.height * logo_ratio)
                        logo_resized = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

                        # Позиция по умолчанию: правый нижний угол
                        logo_pos = (img.width - logo_width - 20, img.height - logo_height - 20)

                        # Переопределение координат, если заданы
                        if logo_coords:
                            try:
                                if isinstance(logo_coords, str):
                                    x_str, y_str = logo_coords.split(",")
                                    logo_pos = (int(x_str.strip()), int(y_str.strip()))
                                elif isinstance(logo_coords, (list, tuple)) and len(logo_coords) == 2:
                                    logo_pos = tuple(map(int, logo_coords))
                            except Exception:
                                logger.warning("Ошибка преобразования координат логотипа: %s", logo_coords)

                        img.paste(logo_resized, logo_pos, logo_resized)
                        logger.info("Добавлен логотип в координаты: %s", logo_pos)
                    except Exception as e:
                        logger.warning("Не удалось загрузить логотип '%s': %s", logo_path, e)

                images.append(img)

            except Exception as e:
                logger.warning("Не удалось обработать изображение %s: %s", filename, e)

    logger.info("Найдено изображений: %d", len(images))
    return images


def generate_overlay(text=None, text_position="bottom",
                     font_size=40, font_color="white", font_path=None,
                     logo_path=None, logo_scale=0.2, logo_coords=None):
    """
    Генерирует отдельный прозрачный слой (оверлей) с текстом и/или логотипом,
    который можно наложить на любое изображение.
    """
    overlay = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Наносим текст (если указан)
    if text:
        try:
            font = ImageFont.truetype(font_path if font_path else "arial.ttf", font_size)
        except Exception as e:
            font = ImageFont.load_default()
            logger.warning("Ошибка загрузки шрифта '%s': %s. Используется шрифт по умолчанию.", font_path, e)

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_position == "top":
                position = ((TARGET_SIZE[0] - text_width) // 2, 50)
            elif text_position == "center":
                position = ((TARGET_SIZE[0] - text_width) // 2, (TARGET_SIZE[1] - text_height) // 2)
            else:
                position = ((TARGET_SIZE[0] - text_width) // 2, TARGET_SIZE[1] - text_height - 50)

            draw.text(position, text, fill=font_color, font=font)
            logger.info("Overlay: добавлен текст '%s' на позицию %s", text, text_position)
        except Exception as e:
            logger.warning("Overlay: ошибка при отрисовке текста '%s': %s", text, e)

    # Наносим логотип (если указан)
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_width = int(TARGET_SIZE[0] * logo_scale)
            logo_ratio = logo_width / logo.width
            logo_height = int(logo.height * logo_ratio)
            logo_resized = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

            logo_pos = (TARGET_SIZE[0] - logo_width - 20, TARGET_SIZE[1] - logo_height - 20)

            if logo_coords:
                try:
                    if isinstance(logo_coords, str):
                        x_str, y_str = logo_coords.split(",")
                        logo_pos = (int(x_str.strip()), int(y_str.strip()))
                    elif isinstance(logo_coords, (list, tuple)) and len(logo_coords) == 2:
                        logo_pos = tuple(map(int, logo_coords))
                except Exception:
                    logger.warning("Overlay: ошибка преобразования координат логотипа: %s", logo_coords)

            overlay.paste(logo_resized, logo_pos, logo_resized)
            logger.info("Overlay: добавлен логотип в координаты: %s", logo_pos)
        except Exception as e:
            logger.warning("Overlay: не удалось загрузить логотип '%s': %s", logo_path, e)

    return overlay
