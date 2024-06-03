from pathlib import Path
import datetime as dt
from typing import override

from ruamel.yaml import YAML
import json

import logging
import logging.config
import logging.handlers

import atexit
atexit

from ruamel.yaml import YAML
import os
import os.path as osp

class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Keep log records with DEBUG and INFO levels.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to filter.

        Returns
        -------
        bool
            True if the log record level is in (DEBUG, INFO), False otherwise.
        """
        return record.levelno <= logging.INFO


LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        """
        Initialize the JSON formatter.

        Parameters
        ----------
        fmt_keys : dict[str, str] | None, optional
            Formatting parameters, by default None.
        """
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            The formatted log record as a JSON string.
        """
        log_dict = self._get_log_dict(record)
        return json.dumps(log_dict, default=str)

    def _get_log_dict(
        self,
        record: logging.LogRecord,
    ) -> dict[str, str]:
        """
        Get the log record as a dictionary.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        dict[str, str]
            The log record as a dictionary.
        """
        fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc  # use UTC time
            ).isoformat(),
        }

        if record.exc_info:
            fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info:
            fields["stack_info"] = self.formatStack(record.stack_info)

        log_dict = {
            key: (
                msg_val
                if (msg_val := fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }
        log_dict.update(fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                log_dict[key] = val

        return log_dict


def setupLoggers():

    # Load the logger configuration
    # Go back one directory to find the config file
    config_path = osp.join("configs", "ulogger.yaml")
    print(config_path)
    try:
        with open(config_path, "r") as f:
            config = YAML(typ="safe").load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f'Config file not found at "{config_path}".')

    # Create the log directory if it doesn't exist
    for handler in config["handlers"].values():
        if handler.get("filename"):
            os.makedirs(osp.dirname(handler["filename"]), exist_ok=True)

    # Configure the logger
    logging.config.dictConfig(config)

    if queue_handler := logging.getHandlerByName("queue_handler"):
        # Manually start the thread for the queue handler
        queue_handler.listener.start()
        # If the program exits, stop the queue handler
        atexit.register(queue_handler.listener.stop)
