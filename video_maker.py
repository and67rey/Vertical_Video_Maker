# video_maker.py
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.VideoClip import VideoClip
import numpy as np
from PIL import Image
import tempfile
import os
import logging
from utils import slide_transition, push_transition

logger = logging.getLogger(__name__)

# Фабрика кадров с эффектом увеличения (zoom-in)
def make_zoom_in_frame_factory(img, overlay, zoom_factor, duration):
    w, h = img.size

    def make_frame(t):
        # Масштаб изображения со временем
        scale = 1 + zoom_factor * t / duration
        new_w, new_h = int(w * scale), int(h * scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Центрируем 1080x1920 в кадре
        left = max((new_w - 1080) // 2, 0)
        top = max((new_h - 1920) // 2, 0)
        cropped = resized.crop((left, top, left + 1080, top + 1920))

        # Наложение оверлея, если задан
        if overlay:
            cropped = cropped.convert("RGBA")
            ov = overlay.copy()
            if ov.size != cropped.size:
                ov = ov.resize(cropped.size, Image.LANCZOS)
            cropped.paste(ov, (0, 0), ov)

        return np.array(cropped.convert("RGB"))

    return make_frame

# Фабрика кадров с эффектом уменьшения (zoom-out)
def make_zoom_out_frame_factory(img, overlay, zoom_out_factor, duration):
    w, h = img.size

    def make_frame(t):
        # Вычисляем масштаб уменьшающегося изображения
        scale = 1 / (1 + zoom_out_factor * (1 - t / duration))
        crop_w, crop_h = int(w * scale), int(h * scale)
        cx, cy = w // 2, h // 2
        left = max(cx - crop_w // 2, 0)
        top = max(cy - crop_h // 2, 0)
        right = min(left + crop_w, w)
        bottom = min(top + crop_h, h)

        # Обрезаем и приводим к размеру 1080x1920
        cropped = img.crop((left, top, right, bottom))
        resized = cropped.resize((1080, 1920), Image.LANCZOS)

        # Наложение оверлея, если задан
        if overlay:
            resized = resized.convert("RGBA")
            ov = overlay.copy()
            if ov.size != resized.size:
                ov = ov.resize(resized.size, Image.LANCZOS)
            resized.paste(ov, (0, 0), ov)

        return np.array(resized.convert("RGB"))

    return make_frame

# Основная функция сборки видео
def create_video_from_images(images, duration, fps, output_path, bitrate=None, crf=None,
                             audio_clip=None, transition="fade", transition_duration=0.5,
                             zoom_factor=0.0, zoom_out_factor=0.0, overlays=None):
    clips = []
    temp_files = []

    logger.info(
        "Параметры: fps=%s, duration=%.2f, transition_duration=%.2f, zoom_factor=%.2f, zoom_out_factor=%.2f",
        fps, duration, transition_duration,
        zoom_factor if zoom_factor is not None else 0.0,
        zoom_out_factor if zoom_out_factor is not None else 0.0)

    if not images:
        logger.error("Список изображений пуст.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        # Сохраняем изображения во временные файлы
        for idx, img in enumerate(images):
            path = os.path.join(tmpdir, f"frame_{idx:03d}.png")
            img.save(path)
            temp_files.append(path)

        num_images = len(images)
        single_loop_duration = num_images * duration

        # Вычисляем количество повторов, если длительность аудио больше одного круга
        if audio_clip:
            total_duration = audio_clip.duration
            epsilon = 1e-6
            if abs(total_duration % single_loop_duration) < epsilon:
                num_loops = int(total_duration // single_loop_duration)
            else:
                num_loops = int(total_duration // single_loop_duration) + 1
        else:
            num_loops = 1

        # Генерируем клипы с применением эффектов
        for loop_idx in range(num_loops):
            for idx in range(num_images):
                path = temp_files[idx]

                if zoom_factor is not None and zoom_factor > 0:
                    base_img = Image.open(path).convert("RGB")
                    overlay = overlays[idx] if overlays else None
                    clip = VideoClip(
                        make_zoom_in_frame_factory(base_img, overlay, zoom_factor, duration),
                        duration=duration
                    ).set_fps(fps)

                elif zoom_out_factor is not None and zoom_out_factor > 0:
                    base_img = Image.open(path).convert("RGB")
                    overlay = overlays[idx] if overlays else None
                    clip = VideoClip(
                        make_zoom_out_frame_factory(base_img, overlay, zoom_out_factor, duration),
                        duration=duration
                    ).set_fps(fps)

                else:
                    # Без zoom-эффекта
                    clip = ImageClip(path).set_duration(duration)

                clips.append(clip)
                logger.debug("Обработано изображение %s", path)

        # Применяем переходы между кадрами
        final_clips = []
        for i in range(len(clips) - 1):
            c1, c2 = clips[i], clips[i + 1]
            if transition == "none":
                final_clips.append(c1)
            elif transition == "fade":
                final_clips.append(c1.fadein(transition_duration).fadeout(transition_duration))
            elif transition == "slide":
                main_part = c1.set_duration(duration - transition_duration)
                slide = slide_transition(c1.set_duration(transition_duration),
                                         c2.set_duration(transition_duration),
                                         duration=transition_duration)
                final_clips.append(main_part)
                final_clips.append(slide)
            elif transition == "push":
                main_part = c1.set_duration(duration - transition_duration)
                push = push_transition(c1.set_duration(transition_duration),
                                       c2.set_duration(transition_duration),
                                       duration=transition_duration)
                final_clips.append(main_part)
                final_clips.append(push)

        final_clips.append(clips[-1].set_duration(duration))  # Последний кадр

        video = concatenate_videoclips(final_clips, method="compose")

        # Установка длительности в соответствие с аудио
        if audio_clip:
            video = video.set_duration(audio_clip.duration)
            logger.info("Добавлена аудиодорожка длительностью %.2f сек", audio_clip.duration)
            video = video.set_audio(audio_clip)

        # Подготовка параметров экспорта
        ffmpeg_params = []
        if crf is not None:
            ffmpeg_params.extend(["-crf", str(crf)])

        logger.info("Экспорт видео: %s", output_path)
        video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            bitrate=None if crf is not None else bitrate,
            ffmpeg_params=ffmpeg_params
        )
