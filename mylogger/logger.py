import pathlib
import datetime as dt
from typing import override

from ruamel.yaml import YAML
import json

import logging
import logging.config
import logging.handlers

import atexit


class NonErrorFilter(logging.Filter):
    @override
    def filter(
        self,
        record: logging.LogRecord
    ) -> bool:
        """
        Filter out log records with DEBUG and INFO levels.

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
    def format(
        self,
        record: logging.LogRecord
    ) -> str:
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
            'message': record.getMessage(),
            'timestamp': dt.datetime.fromtimestamp(
                record.created,
                tz=dt.timezone.utc  # use UTC time
            ).isoformat(),
        }

        if record.exc_info:
            fields['exc_info'] = self.formatException(record.exc_info)
            
        if record.stack_info:
            fields['stack_info'] = self.formatStack(record.stack_info)
            
        log_dict = {
            key: msg_val
            if (msg_val := fields.pop(val, None))
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        log_dict.update(fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                log_dict[key] = val
        
        return log_dict


def setup():
    """
    Set up the loggers.
    Directory "logs" will be created in the current working directory if it does not exist.
    [NOTE] Call this function before using the logger.
    """
    config_path = pathlib.Path(__file__).resolve().parent / 'logger_config.yaml'
    try:
        config = YAML().load(config_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at \"{config_path}\".")
    
    # Logging files are stored in "logs" directory
    try:
        logging.config.dictConfig(config)
    except Exception:
        # If the log directory does not exist, create it and try again
        log_dir = 'logs'
        pathlib.Path(log_dir).mkdir(exist_ok=True)
        logging.config.dictConfig(config)
    
    if (queue_handler := logging.getHandlerByName('queue_handler')):
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)