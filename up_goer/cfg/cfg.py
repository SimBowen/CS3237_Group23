from dotenv import dotenv_values

HOST = "xinming.ddns.net"
USER = "guest"
PASSWORD = dotenv_values()["SERVER_PASSWORD"]
PREDICT_TOPIC = "posture/predict"
CLASSIFY_TOPIC = "posture/classify"
