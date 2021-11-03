import click
import paho.mqtt.client as mqtt
from dotenv import dotenv_values

HOST = "xinming.ddns.net"
USER = "guest"
PASSWORD = dotenv_values["SERVER_PASSWORD"]
PREDICT_TOPIC = "posture/predict"
CLASSIFY_TOPIC = "posture/classify"


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
