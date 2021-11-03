import uuid
from dataclasses import dataclass
from enum import Enum

import click
import paho.mqtt.client as mqtt
from dotenv import dotenv_values

HOST = "xinming.ddns.net"
USER = "guest"
PASSWORD = dotenv_values["SERVER_PASSWORD"]
PREDICT_TOPIC = "posture/predict"
CLASSIFY_TOPIC = "posture/classify"


class Prediction(Enum):
    BAD = 0
    GOOD = 1


class Mock(Enum):
    REAL = 0
    MOCKED = 1


@dataclass(frozen=True)
class ClassifyingData:
    id = uuid.uuid()
    data: list[float]


@dataclass(frozen=True)
class PredictingData:
    id = uuid.uuid()
    prediction: Prediction
    """Confidence level, if available"""
    score: float or None
    mock: Mock


def on_connect(client: mqtt.Client, userdata, flags, result_code):
    click.echo(f"on_connect result_code: {str(result_code)}")
    client.subscribe(PREDICT_TOPIC)
    client.subscribe(CLASSIFY_TOPIC)


def on_message(client: mqtt.Client, userdata, message):
    click.echo(f"on_message {message.payload.decode()}")


def create_client() -> mqtt.Client():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost")
    client.loop_forever()

    return client
