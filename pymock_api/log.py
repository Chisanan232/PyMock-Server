import logging


def init_logger_config(
    format: str = "%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S UTC%z",
    level: int = logging.WARNING,
    encoding: str = "utf-8",
) -> None:
    logging.basicConfig(
        format=format,
        datefmt=datefmt,
        level=level,
        encoding=encoding,
    )
