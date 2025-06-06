# cli.py
import argparse
import logging

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Vertical Video Maker")

    parser.add_argument("--images", type=str, required=True, help="Путь к каталогу с изображениями")
    parser.add_argument("--audio", type=str, help="Путь к аудиофайлу")
    parser.add_argument("--duration", type=float, default=5.0, help="Длительность показа одного изображения в секундах")
    parser.add_argument("--fps", type=int, default=24, help="Кадров в секунду")
    parser.add_argument("--bgcolor", type=str, default="black", help="Цвет фона для изображений")
    parser.add_argument("--output", type=str, default="output.mp4", help="Имя выходного видеофайла")
    parser.add_argument("--bitrate", type=str, help="Битрейт, например, 8000k")
    parser.add_argument("--crf", type=int, help="CRF-параметр качества, например, 28")
    parser.add_argument("--transition", type=str, choices=["none", "fade", "slide", "push"], default="fade", help="Тип перехода между изображениями")
    parser.add_argument("--transition-duration", type=float, default=0.5, help="Длительность перехода в секундах")
    parser.add_argument("--mode", type=str, choices=["basic", "images_loop"], default="basic",
                        help="Режим синхронизации: basic или images_loop")
    parser.add_argument("--zoom", type=float, help="Zoom-in эффект (указать скорость масштабирования, например, 0.1)")
    parser.add_argument("--zoom-out", type=float, help="Zoom-out эффект (указать скорость масштабирования, например, 0.1)")
    parser.add_argument("--text", type=str, help="Текст для наложения на изображение")
    parser.add_argument("--text-position", type=str, choices=["top", "center", "bottom"], default="bottom", help="Позиция текста на изображении")
    parser.add_argument("--font-size", type=int, default=40, help="Размер шрифта")
    parser.add_argument("--font-color", type=str, default="white", help="Цвет шрифта")
    parser.add_argument("--font-path", type=str, help="Путь к .ttf-файлу шрифта")
    parser.add_argument("--logo-path", type=str, help="Путь к файлу логотипа (PNG)")
    parser.add_argument("--logo-scale", type=float, default=0.1, help="Масштаб логотипа относительно ширины")
    parser.add_argument("--logo-coords", type=str, help="Координаты логотипа (x,y) от левого верхнего угла, например: 50,100")

    # Автогенерация обложки
    parser.add_argument("--autocover", nargs="?", const=True, default=None,
                        help="Автоматически создать обложку (без значения — первый кадр, с числом — секунда, например 25)")

    args = parser.parse_args()
    logger.debug("Аргументы командной строки: %s", vars(args))
    return args
