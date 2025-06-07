# runner.py
import time
import logging
import os
from moviepy.editor import AudioFileClip
from image_processor import load_and_process_images, generate_overlay
from audio_processor import load_audio_clip
from video_maker import create_video_from_images

def run_vvm(args):
    # === ИНИЦИАЛИЗАЦИЯ ===
    logger = logging.getLogger(__name__)
    logger.info("==== Запуск VVM через runner.py ====")

    start_time = time.time()  # Засекаем время начала выполнения
    logger.info("Аргументы запуска: %s", vars(args))  # Лог всех параметров

    # === ОБРАБОТКА ПУТИ ВЫВОДА ===
    output_path = args.output
    valid_exts = [".mp4", ".avi", ".mov", ".mkv"]
    base, ext = os.path.splitext(output_path)
    ext = ext.lower()

    # Если указано недопустимое расширение — заменить на .mp4
    if ext and ext not in valid_exts:
        logger.warning("Недопустимое расширение '%s'. Будет автоматически заменено на '.mp4'", ext)
        output_path = base + ".mp4"

    # Если путь — это директория или без расширения
    if not os.path.splitext(output_path)[1]:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            logger.info("Создана директория для вывода: %s", output_path)
        output_path = os.path.join(output_path, "output.mp4")
        logger.info("Имя выходного файла не указано. Используется по умолчанию: %s", output_path)
    else:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info("Создана директория для вывода: %s", output_dir)

    args.output = output_path

    # === ОБРАБОТКА ИЗОБРАЖЕНИЙ ===
    logger.info("Загрузка изображений из каталога: %s", args.images)
    skip_overlay = args.zoom or args.zoom_out  # Если включён zoom — наложение текста/лого позже

    images = load_and_process_images(
        args.images,
        bgcolor=args.bgcolor,
        text=args.text,
        text_position=args.text_position,
        font_size=args.font_size,
        font_color=args.font_color,
        font_path=args.font_path,
        logo_path=args.logo_path,
        logo_scale=args.logo_scale,
        logo_coords=args.logo_coords,
        skip_overlay=skip_overlay
    )

    # === ПОДГОТОВКА ОВЕРЛЕЯ (если зум включён) ===
    overlays = None
    if skip_overlay:
        logger.info("Zoom-режим активен — текст и логотип будут наложены через оверлеи")
        overlay_img = generate_overlay(
            text=args.text,
            text_position=args.text_position,
            font_size=args.font_size,
            font_color=args.font_color,
            font_path=args.font_path,
            logo_path=args.logo_path,
            logo_scale=args.logo_scale,
            logo_coords=args.logo_coords
        )
        overlays = [overlay_img] * len(images)  # Один и тот же оверлей для всех изображений

    if not images:
        logger.error("Не удалось загрузить изображения.")
        return

    # === СОХРАНЕНИЕ ОБЛОЖКИ (если указана опция autocover) ===
    if args.autocover is not None:
        try:
            if isinstance(args.autocover, bool):
                idx = 0  # Первый кадр
            else:
                seconds = float(args.autocover)
                idx = int(seconds // args.duration)

            idx = max(0, min(idx, len(images) - 1))  # Корректировка индекса
            cover_image = images[idx]

            # Определение пути для сохранения обложки
            if args.output:
                thumb_dir = os.path.dirname(args.output)
                thumb_path = os.path.join(thumb_dir, "thumbnail.png") if thumb_dir else "thumbnail.png"
            else:
                thumb_path = "thumbnail.png"

            cover_image.save(thumb_path)
            logger.info("Обложка успешно сохранена: %s (кадр #%d)", thumb_path, idx)
        except Exception as e:
            logger.warning("Ошибка при генерации обложки: %s", e)

    # === ПОДСЧЁТ ДЛИТЕЛЬНОСТИ ВИДЕО ===
    num_images = len(images)
    total_image_duration = num_images * args.duration

    # === ОПРЕДЕЛЕНИЕ ДЛИТЕЛЬНОСТИ АУДИО ===
    audio_duration = 0
    if args.audio:
        try:
            audio_duration = AudioFileClip(args.audio).duration
        except Exception as e:
            logger.warning("Не удалось определить длительность аудио: %s", e)

    # === ВЫБОР РЕЖИМОВ ВИДЕО/АУДИО ===
    image_mode = "basic"
    audio_mode = "cut"

    if args.mode == "images_loop":
        if audio_duration < total_image_duration:
            logger.warning("Аудио короче, будет использоваться loop для audio.")
            audio_mode = "loop"
        else:
            image_mode = "loop"
            total_image_duration = audio_duration
    elif args.mode == "basic":
        audio_mode = "loop" if audio_duration < total_image_duration else "cut"

    logger.info("Режимы: mode=%s, image_mode=%s, audio_mode=%s", args.mode, image_mode, audio_mode)

    # === ЗАГРУЗКА И ОБРАБОТКА АУДИО ===
    audio_clip = None
    if args.audio:
        try:
            audio_clip = load_audio_clip(
                path=args.audio,
                mode=audio_mode,
                video_duration=total_image_duration
            )
        except Exception as e:
            logger.error("Ошибка при обработке аудиофайла: %s", e)

    # === СОЗДАНИЕ ВИДЕО ===
    create_video_from_images(
        images=images,
        duration=args.duration,
        fps=args.fps,
        output_path=args.output,
        bitrate=args.bitrate,
        crf=args.crf,
        audio_clip=audio_clip,
        transition=args.transition,
        transition_duration=args.transition_duration,
        zoom_factor=args.zoom,
        zoom_out_factor=args.zoom_out,
        overlays=overlays
    )

    # === ЗАВЕРШЕНИЕ ===
    end_time = time.time()
    logger.info("Видео успешно создано: %s", args.output)
    logger.info("Общее время выполнения: %.2f сек", end_time - start_time)
