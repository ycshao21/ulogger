# mylogger
## Requirements
```
python >= 3.12
ruamel.yaml
```

## How to use it?
Place the `mylogger` folder in your working directory, and add code like this before you use the logger.
```py
import mylogger
mylogger.setup()
```
Then you can import logging and get loggers.

All the logging history will be saved in the `logs` folder as jsonl files, so you can use json parser to get detailed information.
You can keep 20 files at most, each of which does not exceed 5MB. And the oldest file will be deleted if more information is to be appended. You can customize by modifying `mylogger/logger_config.yaml`.