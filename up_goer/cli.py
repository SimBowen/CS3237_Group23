import asyncio

import click
from bleak import BleakScanner


@click.group()
def run():
    pass


@run.command()
def discover():
    asyncio.run(discover())


async def discover():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
