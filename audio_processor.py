# audio_processor.py
from moviepy.editor import AudioFileClip, concatenate_audioclips
import logging

logger = logging.getLogger(__name__)

def load_audio_clip(path, mode="cut", video_duration=0, fade_in_duration=1.0, fade_out_duration=1.0):
    try:
        logger.info("Загрузка аудио: %s", path)
        clip = AudioFileClip(path)
        logger.debug("Длительность исходного аудио: %.2f сек", clip.duration)

        if mode == "cut":
            if clip.duration > video_duration:
                logger.debug("Аудио будет обрезано до %.2f сек", video_duration)
                clip = clip.subclip(0, video_duration)
            clip = clip.audio_fadein(fade_in_duration).audio_fadeout(fade_out_duration)
            logger.info("Применен режим обработки аудио: cut, с эффектами fade-in и fade-out")

        elif mode == "loop":
            repeat_count = int(video_duration // clip.duration) + 1
            logger.debug("Аудио повторено %d раз", repeat_count)
            clips = [clip] * repeat_count
            clip = concatenate_audioclips(clips).subclip(0, video_duration)
            clip = clip.audio_fadein(fade_in_duration).audio_fadeout(fade_out_duration)
            logger.info("Применен режим обработки аудио: loop, с эффектами fade-in и fade-out")

        else:
            logger.warning("Неизвестный режим обработки аудио: %s", mode)

        return clip

    except Exception as e:
        logger.exception("Ошибка при обработке аудиофайла: %s", e)
        raise
