import dotenv
import paho.mqtt.client as mqtt
from dotenv import dotenv_values

HOST = "xinming.ddns.net"
USER = "guest"
PASSWORD = dotenv_values["SERVER_PASSWORD"]
PREDICT_TOPIC = "posture/predict"
CLASSIFY_TOPIC = "posture/classify"


def on_connect(client: mqtt.Client, userdata, flags, result_code):
    print(f"connected with rc: {str(result_code)}")
    client.subscribe(TOPIC)
    client.publish("hello/world", "test")


def on_message(client: mqtt.Client, userdata, message):
    print(f"Received {message.payload.decode()}")


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost")
client.loop_forever()
