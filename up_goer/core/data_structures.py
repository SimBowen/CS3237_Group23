import uuid
from dataclasses import astuple, dataclass
from enum import Enum

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class SensorData:
    x: float
    y: float
    z: float

    def __iter__(self):
        return iter(astuple(self))

    def is_valid(self):
        return self.x != 0 and self.y != 0 and self.z != 0


@dataclass_json
@dataclass(frozen=True)
class SensorTagData:
    address: str
    timestamp: float
    gyroscope: SensorData
    accelerometer: SensorData
    magnetometer: SensorData

    def is_valid(self):
        return (
            self.gyroscope.is_valid()
            and self.accelerometer.is_valid()
            and self.magnetometer.is_valid()
        )


@dataclass_json
@dataclass(frozen=True)
class GatewayData:
    sensor_tags: list[SensorTagData]


class Prediction(Enum):
    BAD = 0
    GOOD = 1


class Mock(Enum):
    REAL = 0
    MOCKED = 1


@dataclass_json
@dataclass(init=False)
class ClassifyingData:
    data: list[float]
    id: uuid.UUID

    def __init__(self, data):
        self.data = data
        self.id = uuid.uuid4()


@dataclass_json
@dataclass(frozen=True)
class PredictingData:
    id: str
    prediction: Prediction
    """Confidence level, if available"""
    score: float or None
    mock: Mock
