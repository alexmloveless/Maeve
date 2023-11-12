from maeve.models.core import LogConst
from collections import deque
from datetime import datetime


class Logger:
    def __init__(
            self,
            log_level: str = None,
            log_location: str = None,
            log_maxlen: int = 1e+5
    ):
        self.g = LogConst()

        log_location = log_location if log_location else self.g.defualt_loc
        log_level = log_level if log_level else self.g.default_level
        self.loc = log_location

        self._levels = {v: level for level, v in enumerate(self.g.levels)}
        self.level = self._levels[log_level]
        self._log = deque([], int(log_maxlen))

    def debug(self, *args, **kwargs):
        self.log("DEBUG", *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log("INFO", *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log("WARNING", *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log("ERROR", *args, **kwargs)

    def critical(self, *args, **kwargs):
        self.log("CRITICAL", *args, **kwargs)

    def log(self, level, message, detail=''):
        if self._levels[level] >= self.level:

            if self.loc in ["catalogue", "both"]:
                self.add_to_log(level, message, detail)

            if self.loc in ["stdout", "both"]:
                print(f"{datetime.now()} {level} {message} {detail}")

    def add_to_log(self, level: str, source: str, message: str, detail: str = None):
        self._log.append({
            self.g.timestamp_label: datetime.now(),
            self.g.level_label: level,
            self.g.source_label: source,
            self.g.message_label: message,
            self.g.detail_label: detail
        })

    def get_log(self, fmt="df"):
        if fmt in ["df", "dataframe"]:
            import pandas as pd
            return pd.DataFrame.from_records(self._log)
        else:
            return self._log

