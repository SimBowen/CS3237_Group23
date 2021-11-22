import os
from pathlib import Path
from time import sleep

import arrow
from paho.mqtt.client import Client
from up_goer.cfg import cfg
from up_goer.core.data_structures import ClassifyingData, PredictingData


class Spammer:
    def __init__(self):
        self.publisher = Client()
        self.publisher.username_pw_set(cfg.USER, cfg.PASSWORD)
        self.publisher.connect(cfg.HOST)

    def blast(self, path: Path):
        with open(path, "r") as file:
            for line in file:
                data = line.split(",")
                data = ClassifyingData(data[1:4])
                self._send(data)

    def _send(self, data: ClassifyingData):
        print("sent", data)
        data = data.to_json().encode()
        self.publisher.publish(cfg.CLASSIFY_TOPIC, payload=data)
        sleep(0.1)
