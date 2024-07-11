import logging

import os


def get_logger(logger_name):
    try:
        logging.config.fileConfig(os.path.expanduser("~/.config/gnss-ui/log.ini"))
    except Exception as e:
        log_filename = os.path.expanduser("~/.gnss-ui") + "/gnss-ui.log"
        DEFAULT_LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "brief": {
                    "datefmt": "%H:%M:%S",
                    "format": "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                },
                "verbose": {
                    "format": "%(levelname)-8s; [%(process)d]; %(threadName)s; %(name)s; %(module)s:%(funcName)s;%(lineno)d"
                    ": %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    # 'stream': 'ext://sys.stdout'
                },
                "file_handler": {
                    "level": "INFO",
                    "class": "logging.FileHandler",
                    "formatter": "brief",
                    "filename": log_filename,
                    # 'mode': 'a',
                    # 'encoding': 'utf-8',
                },
            },
            "loggers": {
                "app": {
                    "level": "INFO",
                    "handlers": ["console", "file_handler"],
                },
                "datamodel": {
                    "level": "INFO",
                    "handlers": ["console", "file_handler"],
                },
                "gpsd": {
                    "level": "INFO",
                    "handlers": ["console", "file_handler"],
                },
                "ttyc": {
                    "level": "INFO",
                    "handlers": ["console", "file_handler"],
                },
            },
        }
        logging.config.dictConfig(DEFAULT_LOGGING)

    return logging.getLogger(logger_name)
