import json
import uuid
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SensorData:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class MovementSensorData:
    timestamp: float
    gyroscope: SensorData
    accelerometer: SensorData
    magnetometer: SensorData


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
