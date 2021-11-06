import asyncio

import click
from bleak import BleakScanner

from up_goer.cfg import cfg
from up_goer.computer.computer import Computer
from up_goer.gateway.gateway import Gateway
from up_goer.logger.logger import Logger
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


@run.command()
def gateway():
    gateway = Gateway([cfg.TAG_ADDRESS_1, cfg.TAG_ADDRESS_2, cfg.TAG_ADDRESS_3])
    asyncio.run(gateway.main())


@run.command()
def computer():
    computer = Computer()
    computer.gateway_subscriber.loop_forever()


@run.command()
def test_shawn():
    # Tag 3
    address = "6D0713AD-8093-474D-AC67-3BAFE1D2757A"
    gateway = Gateway([address])
    asyncio.run(gateway.main())


@run.command()
@click.option("--filename", prompt=True, type=click.Path())
def generate_csv(filename: str):
    logger = Logger(filename)
    logger.computer_subscriber.loop_forever()
