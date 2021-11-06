import json
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
    if message.topic != PREDICT_TOPIC:
        return

    predicting_data = message.payload.decode()
    predicting_data = json.loads(predicting_data)
    predicting_data = PredictingData(
        id=predicting_data["id"],
        prediction=Prediction(predicting_data["prediction"]),
        score=predicting_data["score"],
        mock=predicting_data["mock"],
    )
    click.echo(predicting_data)


def create_client() -> mqtt.Client():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    return client
