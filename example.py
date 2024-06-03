import ulogger
ulogger.setupLoggers()

import logging
logger = logging.getLogger("test")


def test_logger():
    logger.debug("This is a debug message.", extra={'acc': 0.95})
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    try:
        1 / 0
    except Exception:
        logger.exception("An exception was thrown!")


if __name__ == '__main__':
    test_logger()