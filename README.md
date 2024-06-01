# ulogger
## Requirements
```
python >= 3.12
ruamel.yaml
```

## How to use it
Add the following lines to the python scripts where you want to log messages:
```py
import mylogger
mylogger.setup(name="<name_of_logging_folder>")

import logging 
logger = logging.getLogger("<logger_name>")
```

All the logging history will be saved as `.jsonl` files in the `logs` directory. You can specify the name of each logging subfolder, as shown in the code above. If not, it defaults to the current timestamp. For details, check out `example.py`

Each log file will rotate once it exceeds 2MB. You can customize the logger by modifying `configs/ulogger.yaml`.