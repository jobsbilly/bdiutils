import logging
import pathlib
import socket

from IPython.display import display
import pandas as pd
import requests

import bdiutils.logging

def notebook_name_and_id() -> tuple[str, str]:
    ip = socket.gethostbyname(socket.gethostname())
    resp = requests.get(f"http://{ip}:9000/api/sessions").json()[0]
    notebook_name = resp["name"]
    notebook_id = resp["path"].split("=")[1]
    return notebook_name, notebook_id

def init_loggers(
        log_file_path: str | pathlib.Path | None,
        level=logging.INFO,
        attr: str = "name") -> logging.Logger:
    bdiutils.logging.init_loggers(log_file_path, level, attr)
    _, notebook_id = notebook_name_and_id()
    logger_name = f"colab/{notebook_id}"
    return logging.getLogger(logger_name)

def describe(dataset: pd.DataFrame, label: str = "dataframe", skip_mem_usage: bool = False,
             skip_null_counts: bool = False, skip_statistics: bool = False, sample_n: int = 5) -> None:
    print(f"\n---------- {label.upper()}: Summary ----------")
    dataset.info(verbose=True, memory_usage="deep")
    if not skip_mem_usage:
        print(f"\n---------- {label.upper()}: Memory Usage (bytes) ----------"
              f"\n{dataset.memory_usage(deep=True).sort_values(ascending=False)}")
    if not skip_null_counts:
        print(f"\n---------- {label.upper()}: NULL value counts ----------"
              f"\n{dataset.isnull().sum()}")
    if not skip_statistics:
        print(f"\n---------- {label.upper()}: Statistics ----------")
        # display(dataset.describe(include='all', datetime_is_numeric=True))
        display(dataset.describe(include='all'))
    if sample_n > 0:
        print(f"\n---------- {label.upper()}: Sample rows ----------")
        display(dataset.sample(sample_n))
