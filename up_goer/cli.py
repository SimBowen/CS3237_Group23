import asyncio

import click
from bleak import BleakScanner

from up_goer.sensors import client, main


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
@click.option("--address1", prompt=True, type=str)
@click.option("--address2", prompt=True, type=str)
@click.option("--address3", prompt=True, type=str)
def gateway(address1: str, address2: str, address3: str):
    client.connect("localhost")
    asyncio.run(main())
    client.loop_forever()
