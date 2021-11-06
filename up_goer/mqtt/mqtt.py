import uuid
from dataclasses import dataclass
from enum import Enum

import click
import paho.mqtt.client as mqtt
from up_goer.cfg.cfg import CLASSIFY_TOPIC, PREDICT_TOPIC


class Prediction(Enum):
    BAD = 0
    GOOD = 1


class Mock(Enum):
    REAL = 0
    MOCKED = 1


@dataclass(frozen=True)
class ClassifyingData:
    id = uuid.uuid4()
    data: list[float]


@dataclass(frozen=True)
class PredictingData:
    id: str
    prediction: Prediction
    """Confidence level, if available"""
    score: float or None
    mock: Mock


def on_connect(client: mqtt.Client, userdata, flags, result_code):
    click.echo(f"on_connect result_code: {str(result_code)}")
    client.subscribe(PREDICT_TOPIC)
    client.subscribe(CLASSIFY_TOPIC)


def on_message(client: mqtt.Client, userdata, message):
    predicting_data = message.payload.decode()
    predicting_data = PredictingData(**predicting_data)
    click.echo(predicting_data)


def create_client() -> mqtt.Client():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    return client
