import os
from pathlib import Path

import arrow
from paho.mqtt.client import Client
from up_goer.cfg import cfg
from up_goer.core.data_structures import ClassifyingData


def _write_csv(data: str, filename: str):
    path = Path(filename)
    mode = "a" if os.path.exists(path.parent) else "w"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode=mode) as file:
        file.write(data)


def _save_csv(data: list[float], filename: str):
    time = arrow.now().timestamp()
    stringified_data = list(map(lambda x: str(x), data))
    stringified_data.insert(0, str(time))
    output = ",".join(stringified_data)
    _write_csv(output + "\n", filename)


class Logger:
    def __init__(self, filename: str):
        self.filename = filename
        self.computer_subscriber = Client()
        self.computer_subscriber.on_connect = self.on_connect
        self.computer_subscriber.on_message = self.on_message
        self.computer_subscriber.connect(cfg.COMPUTER_HOST)

    def on_connect(self, client: Client, userdata, flags, result_code):
        if client is not self.computer_subscriber:
            return
        client.subscribe(cfg.LOGGER_TOPIC)

    def on_message(self, client: Client, userdata, message):
        if client is not self.computer_subscriber:
            return
        if message.topic != cfg.LOGGER_TOPIC:
            return
        payload = message.payload.decode()
        data = ClassifyingData.from_json(payload)
        self._parse(data)

    def _parse(self, data: ClassifyingData):
        _save_csv(data.data, self.filename)
        print(data.data)
