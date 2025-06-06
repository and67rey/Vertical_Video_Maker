# logger_setup.py
import logging
import sys
from pathlib import Path

def setup_logging():
    # Получаем корневой логгер. Он будет использоваться всеми модулями,
    # если они вызывают logging.getLogger(__name__).
    logger = logging.getLogger()

    # Устанавливаем минимальный уровень логирования: INFO.
    # Это значит, что DEBUG-сообщения игнорируются, но INFO и выше (WARNING, ERROR, CRITICAL) будут логироваться.
    logger.setLevel(logging.INFO)

    # Создаём форматтер — он определяет формат записей в логах.
    # Пример: "2025-06-02 12:34:56 - INFO - Сообщение"
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Создаём потоковый обработчик (StreamHandler), который пишет логи в стандартный вывод (консоль).
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)  # Применяем форматтер к консольному выводу

    # Создаём обработчик для записи логов в файл.
    # Файл будет называться "vvm.log", логирование ведётся в режиме добавления ('a').
    log_file = Path("vvm.log")
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)  # Применяем форматтер к файловому выводу

    # Добавляем обработчики к логгеру, если они ещё не были добавлены.
    # Это предотвращает дублирование логов при повторной инициализации.
    if not logger.handlers:
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    # Возвращаем сконфигурированный логгер (необязательно, но удобно при тестировании)
    return logger
