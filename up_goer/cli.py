import asyncio

import click
from bleak import BleakScanner


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
