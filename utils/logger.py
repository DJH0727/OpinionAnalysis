# utils/logger.py

import logging
import sys

class Logger:
    COLOR_MAP = {
        "DEBUG": "\033[94m",   # 蓝色
        "INFO": "\033[92m",    # 绿色
        "WARNING": "\033[93m", # 黄色
        "ERROR": "\033[91m",   # 红色
        "RESET": "\033[0m",    # 重置颜色
    }

    def __init__(self, name="default", level="info"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.propagate = False  # 避免重复打印

        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        console_handler.setFormatter(self.ColoredFormatter(formatter))
        self.logger.addHandler(console_handler)

    class ColoredFormatter(logging.Formatter):
        def __init__(self, base_formatter):
            super().__init__()
            self.base_formatter = base_formatter

        def format(self, record):
            levelname = record.levelname
            color = Logger.COLOR_MAP.get(levelname, Logger.COLOR_MAP["RESET"])
            reset = Logger.COLOR_MAP["RESET"]
            msg = self.base_formatter.format(record)
            return f"{color}{msg}{reset}"

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
