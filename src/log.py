import sys
import os
from loguru import logger

# Создаем папку logs, если её еще нет (чтобы не было ошибок при первом запуске)
if not os.path.exists("logs"):
    os.makedirs("logs")

def setup_logger():
    # Удаляем стандартный обработчик (чтобы логи не дублировались)
    logger.remove()

    # 1. Вывод в КОНСОЛЬ (все сообщения от INFO и выше)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # 2. Файл для ОПОВЕЩЕНИЙ (INFO) и ПРЕДУПРЕЖДЕНИЙ (WARNING)
    logger.add(
        "logs/info.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
        level="INFO",
        rotation="5 MB",         # Создавать новый файл, когда этот достигнет 5 МБ
        retention="14 days",     # Хранить логи 2 недели
        encoding="utf-8",
        # Фильтруем: пускаем сюда только INFO и WARNING, чтобы ошибки шли в свой файл
        filter=lambda record: record["level"].name in ["INFO", "WARNING"]
    )

    # 3. Файл только для ОШИБОК (ERROR)
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="1 month",     # Ошибки храним дольше (1 месяц)
        encoding="utf-8"
    )

# Запускаем настройку
setup_logger()

# Экспортируем настроенный логгер
__all__ = ["logger"]