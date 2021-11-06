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
def gateway():
    client.connect("localhost")
    asyncio.run(main())
    client.loop_forever()
