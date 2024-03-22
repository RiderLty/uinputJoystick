import logging
import coloredlogs

from .tools import CallbackHandler



logger = logging.getLogger(f'{"main"}:{"loger"}')
fmt = f"🤖%(asctime)s .%(levelname)s %(message)s"
coloredlogs.install(
    level=logging.DEBUG, logger=logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt,
)
formatter = logging.Formatter(fmt = f"🤖%(asctime)s .%(levelname)s \t%(message)s" , datefmt='%m-%d %H:%M:%S')

    
def initUvicornLogger():
    LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
    for logger_name in LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        fmt = f"🌏%(asctime)s .%(levelname)s %(message)s"  # 📨
        coloredlogs.install(
            level=logging.WARN, logger=logging_logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt
        )


def addLogCallback(log_callback):
    handler = CallbackHandler(callback=log_callback)
    handler.setFormatter(formatter)
    logger.addHandler(handler)