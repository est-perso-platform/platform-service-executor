import logging
import sys


def get_logger(level: str = "DEBUG") -> None:

    logger = logging.getLogger("platform_service_executor")
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logger.setLevel(level)

    return logger
