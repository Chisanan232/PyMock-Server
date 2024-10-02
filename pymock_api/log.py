import logging

DEBUG_LEVEL_LOG_FORMAT: str = "%(asctime)s [%(levelname)s] (%(name)s - %(funcName)s at %(lineno)d): %(message)s"
DEBUG_LEVEL_LOG_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S UTC%z"


def init_logger_config(
    format: str = "",
    datefmt: str = "",
    level: int = logging.WARNING,
    encoding: str = "utf-8",
) -> None:
    if level is logging.DEBUG:
        format = DEBUG_LEVEL_LOG_FORMAT
        datefmt = DEBUG_LEVEL_LOG_DATETIME_FORMAT

    logging.basicConfig(
        format=format,
        datefmt=datefmt,
        level=level,
        encoding=encoding,
    )
