# utils.py
from moviepy.editor import CompositeVideoClip

def slide_transition(old_clip, new_clip, duration=0.5):
    """Переход типа 'slide' — новое изображение сдвигает старое справа налево."""
    w, h = old_clip.size
    # Старое изображение остаётся неподвижным
    static_old = old_clip.set_position(("center", "center"))
    # Новое изображение выезжает справа налево
    sliding_new = new_clip.set_position(lambda t: (w * (1 - t / duration), 0)).set_start(0)
    return CompositeVideoClip([static_old, sliding_new], size=(w, h)).set_duration(duration)

def push_transition(clip1, clip2, duration=1.0):
    """Переход типа 'push' — старое изображение уезжает влево, новое заезжает справа."""
    w, h = clip1.size
    out_clip = clip1.set_position(lambda t: (-w * t / duration, 0)).set_end(duration)
    in_clip = clip2.set_position(lambda t: (w - w * t / duration, 0)).set_start(0)
    return CompositeVideoClip([out_clip, in_clip], size=(w, h)).set_duration(duration)
