import os
from pathlib import Path

import arrow


def _write_csv(data: str, filename: str):
    path = Path(filename)
    mode = "a" if os.path.exists(path.parent) else "w"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode=mode) as file:
        file.write(data)


def save_csv_functor(data: list[float], filename: str):
    time = arrow.now().timestamp()
    stringified_data = list(map(lambda x: str(x), data))
    stringified_data.insert(0, str(time))
    output = ",".join(stringified_data)
    _write_csv(output + "\n", filename)
