import asyncio
import json
import uuid

import click
from bleak import BleakScanner

from up_goer.cc2650 import cc2650
from up_goer.mqtt.mqtt import CLASSIFY_TOPIC, create_client

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
    mqtt_client.publish(CLASSIFY_TOPIC, json.dumps(data))


@run.command()
@click.option("--address1", prompt=True, type=str)
@click.option("--address2", prompt=True, type=str)
@click.option("--address3", prompt=True, type=str)
def gateway(address1: str, address2: str, address3: str):
    mqtt_client.connect("localhost")
    asyncio.run(cc2650.main(_functor))
    print("are u blocking")
    mqtt_client.loop_forever()
