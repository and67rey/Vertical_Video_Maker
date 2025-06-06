import logging
from logger_setup import setup_logging


def test_setup_logging_creates_logfile(tmp_path, monkeypatch):
    """Проверка: setup_logging создаёт лог-файл и записывает сообщение"""

    # Очистить существующие обработчики, чтобы setup_logging() добавил новые
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    monkeypatch.chdir(tmp_path)

    logger = setup_logging()
    test_msg = "Test log write"
    logger.info(test_msg)

    log_path = tmp_path / "vvm.log"
    assert log_path.exists()

    for h in logger.handlers:
        if hasattr(h, "flush"):
            h.flush()

    with open(log_path, "r", encoding="utf-8") as f:
        contents = f.read()

    assert test_msg in contents
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 2
