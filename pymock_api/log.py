import logging
import sys

DEBUG_LEVEL_LOG_FORMAT: str = "%(asctime)s [%(levelname)8s] (%(name)s - %(funcName)s at %(lineno)d): %(message)s"
DEBUG_LEVEL_LOG_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S UTC%z"


def init_logger_config(
    formatter: str = "",
    datefmt: str = "",
    level: int = logging.INFO,
    encoding: str = "utf-8",
) -> None:
    if level == logging.DEBUG:
        formatter = DEBUG_LEVEL_LOG_FORMAT
        datefmt = DEBUG_LEVEL_LOG_DATETIME_FORMAT

    if sys.version_info >= (3, 9):
        logging.basicConfig(
            format=formatter,
            datefmt=datefmt,
            level=level,
            encoding=encoding,
        )
    else:
        logging.basicConfig(
            format=formatter,
            datefmt=datefmt,
            level=level,
        )
