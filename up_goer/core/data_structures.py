import uuid
from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class SensorData:
    x: float
    y: float
    z: float


@dataclass_json
@dataclass(frozen=True)
class SensorTagData:
    address: str
    timestamp: float
    gyroscope: SensorData
    accelerometer: SensorData
    magnetometer: SensorData


# TODO: Override (de)serialisation
class Prediction(Enum):
    BAD = 0
    GOOD = 1


# TODO: Override (de)serialisation
class Mock(Enum):
    REAL = 0
    MOCKED = 1


@dataclass_json
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
