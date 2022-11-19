#!/usr/bin/env python3
# fmt: off

import logging

from bridgekeeper.utils.colors import text_colors


class LoggingLevels:
    """Logging level outputs"""

    CRITICAL = f"{text_colors.FAIL}%s{text_colors.ENDC}" % "crit"     # 50
    ERROR    = f"{text_colors.FAIL}%s{text_colors.ENDC}" % "fail"     # 40
    WARNING  = f"{text_colors.WARNING}%s{text_colors.ENDC}" % "warn"  # 30
    INFO     = f"{text_colors.OKGREEN}%s{text_colors.ENDC}" % "info"  # 20
    DEBUG    = f"{text_colors.OKBLUE}%s{text_colors.ENDC}" % "debg"   # 10


def init_logger(debug: bool):
    """Initialize program logging

    Arguments:
        debug: if debugging is enabled
    """
    if debug:
        logging_level = logging.DEBUG
        logging_format = "[%(asctime)s] %(levelname)-5s | %(filename)18s:%(lineno)-4s | %(message)s"

    else:
        logging_level = logging.INFO
        logging_format = "[%(asctime)s] %(levelname)-5s | %(message)s"

    logging.basicConfig(format=logging_format, level=logging_level)

    # Update log level names with colorized output
    logging.addLevelName(logging.CRITICAL, LoggingLevels.CRITICAL)  # 50
    logging.addLevelName(logging.ERROR,    LoggingLevels.ERROR)     # 40
    logging.addLevelName(logging.WARNING,  LoggingLevels.WARNING)   # 30
    logging.addLevelName(logging.INFO,     LoggingLevels.INFO)      # 20
    logging.addLevelName(logging.DEBUG,    LoggingLevels.DEBUG)     # 10
