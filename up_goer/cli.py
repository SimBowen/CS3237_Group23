import asyncio
import json
import os
import time
import uuid
from pathlib import Path

import click
from bleak import BleakScanner

from up_goer.cfg import cfg
from up_goer.gateway.gateway import Gateway
from up_goer.mqtt.mqtt import create_client

# TODO: Global quick hack to avoid async issues for now.
mqtt_client = create_client()


@click.group()
def run():
    pass


async def _discover():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


@run.command()
def discover():
    asyncio.run(_discover())


def _functor(data: list[float]):
    data = {
        "id": str(uuid.uuid4()),
        "data": data,
    }
    mqtt_client.publish(cfg.CLASSIFY_TOPIC, json.dumps(data))


def _save_csv_functor(data: list[float]):
    data = {
        "id": str(uuid.uuid4()),
        "data": data,
    }
    data = json.dumps(data)
    _write_csv(data + "\n", "data.csv")


@run.command()
def gateway():
    gateway = Gateway([cfg.TAG_ADDRESS_1, cfg.TAG_ADDRESS_2, cfg.TAG_ADDRESS_3])
    mqtt_client.username_pw_set(cfg.USER, cfg.PASSWORD)
    mqtt_client.connect(cfg.HOST)
    asyncio.run(gateway.main(_functor))
    # asyncio.run(gateway.main(_save_csv_functor))
    mqtt_client.loop_forever()


def _write_csv(data: str, filename: str):
    path = Path(filename)
    mode = "a" if os.path.exists(path.parent) else "w"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode=mode) as file:
        file.write(data)


def _save_data(yaw_1, yaw_2, yaw_3):
    str_time = time.strftime("%H:%M:%S")
    yaw1 = str(yaw_1)
    yaw2 = str(yaw_2)
    yaw3 = str(yaw_3)
    data = ",".join([str_time, yaw1, yaw2, yaw3])
    data = f"\n{data}"
    _write_csv(data, "data.csv")


def listen_mqtt():
    mqtt_client.username_pw_set(cfg.USER, cfg.PASSWORD)
    mqtt_client.connect(cfg.HOST)
    mqtt_client.loop_forever()


# TODO: Quick hack for Xin Ming to run without poetry
if __name__ == "__main__":
    gateway()
