import os
import datetime as dt

from ruamel.yaml import YAML
import json

import logging
import logging.config


class NonErrorFilter(logging.Filter):
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
    Call this function where the loggers are to be used.

    Raises
    ------
    FileNotFoundError
        If the logger configuration file is not found.
    """
    config_path = 'logger_config.yaml'
    config_path = os.path.join(os.path.dirname(__file__), config_path)

    if os.path.exists(config_path):
        config = YAML().load(open(config_path))
    else:
        raise FileNotFoundError(f"Config file not found at \"{config_path}\".")
    
    # Log files are stored in "logs" directory
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up the logger
    logging.config.dictConfig(config)