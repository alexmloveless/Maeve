import logging

class Util:

    def get_logger(self, name: str, log_level: str = "WARNING"):

        LOG_LEVELS = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        logger = logging.getLogger(name)
        if log_level:
            logger.setLevel(LOG_LEVELS[log_level])
        return logger
