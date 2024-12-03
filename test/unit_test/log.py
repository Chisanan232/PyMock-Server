import logging
import sys
from unittest.mock import patch

import pytest

from pymock_api.log import (
    DEBUG_LEVEL_LOG_DATETIME_FORMAT,
    DEBUG_LEVEL_LOG_FORMAT,
    init_logger_config,
)


@pytest.mark.parametrize("level", [logging.INFO, logging.WARN, logging.WARNING, logging.ERROR])
def test_not_debug_level_log_config(level: int):
    formatter = "this is customize format"
    datefmt = "this is customize datetime format"

    with patch("logging.basicConfig") as logging_config:
        init_logger_config(
            formatter=formatter,
            datefmt=datefmt,
            level=level,
            encoding="utf-8",
        )

    if sys.version_info >= (3, 9):
        logging_config.assert_called_once_with(
            format=formatter,
            datefmt=datefmt,
            level=level,
            encoding="utf-8",
        )
    else:
        logging_config.assert_called_once_with(
            format=formatter,
            datefmt=datefmt,
            level=level,
        )


def test_debug_level_log_config():
    with patch("logging.basicConfig") as logging_config:
        init_logger_config(
            level=logging.DEBUG,
            encoding="utf-8",
        )

    if sys.version_info >= (3, 9):
        logging_config.assert_called_once_with(
            format=DEBUG_LEVEL_LOG_FORMAT,
            datefmt=DEBUG_LEVEL_LOG_DATETIME_FORMAT,
            level=logging.DEBUG,
            encoding="utf-8",
        )
    else:
        logging_config.assert_called_once_with(
            format=DEBUG_LEVEL_LOG_FORMAT,
            datefmt=DEBUG_LEVEL_LOG_DATETIME_FORMAT,
            level=logging.DEBUG,
        )
