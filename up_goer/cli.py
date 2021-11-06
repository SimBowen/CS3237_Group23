import asyncio
import json
import uuid

import click
from bleak import BleakScanner

from up_goer.cfg import cfg
from up_goer.csv import csv
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


@run.command()
def gateway():
    gateway = Gateway([cfg.TAG_ADDRESS_1, cfg.TAG_ADDRESS_2, cfg.TAG_ADDRESS_3])
    mqtt_client.username_pw_set(cfg.USER, cfg.PASSWORD)
    mqtt_client.connect(cfg.HOST)
    asyncio.run(gateway.main(_functor))
    mqtt_client.loop_forever()


@run.command()
@click.option("--filename", prompt=True, type=click.Path())
def generate_csv(filename: str):
    def functor(data: list[float]):
        csv.save_csv_functor(data, filename)

    gateway = Gateway([cfg.TAG_ADDRESS_1, cfg.TAG_ADDRESS_2, cfg.TAG_ADDRESS_3])
    asyncio.run(gateway.main(functor))
