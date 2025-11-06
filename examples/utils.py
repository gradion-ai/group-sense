import logging


def configure_logging(
    level: int = logging.DEBUG,
    logger_names: list[str] | None = None,
):
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    if logger_names is None:
        logger_names = ["group_sense", "examples", "__main__"]

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not logger.handlers:
            logger.addHandler(handler)
