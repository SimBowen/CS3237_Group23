# Mqtt Protocol For Posture Prediction

## Classifying

**Data**

```json
{
  "id": "a6b32309-35e9-4a0e-91db-0d0cfe75c1de",
  "data": [80.2, 90.3, 109.1]
}
```

Use `uuid.uuid4()` to generate unique id
Sequence of data is important

## Predicting

**Data**

```json
{
  "id": "a6b32309-35e9-4a0e-91db-0d0cfe75c1de",
  "prediction": 0,
  "score": 1.0,
  "mock": 1
}
```

`"prediction": 0` Bad Posture

`"prediction": 1` Good Posture

`"mock": 0` Prediction is real

`"mock": 1` Prediction is mocked

`"score"` Confidence level, if available

## MQTT Config

```python
HOST = 'xinming.ddns.net'
USER = 'guest'
PASSWORD = '<ASK ME>'
PREDICT_TOPIC = 'posture/predict'
CLASSIFY_TOPIC = 'posture/classify'
```
