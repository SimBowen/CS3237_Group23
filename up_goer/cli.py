import asyncio
from os import name
from pathlib import Path

import typer
from bleak import BleakScanner

from up_goer.cfg import cfg
from up_goer.computer.computer import Computer
from up_goer.gateway.gateway import Gateway
from up_goer.logger.logger import Logger

app = typer.Typer()
gateway = typer.Typer()
app.add_typer(gateway, name="gateway")


async def _discover():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


@app.command()
def discover():
    asyncio.run(_discover())


@gateway.command(name="all")
def gateway_all():
    gateway = Gateway([cfg.TAG_ADDRESS_1, cfg.TAG_ADDRESS_2, cfg.TAG_ADDRESS_3])
    asyncio.run(gateway.main())


@gateway.command(name="single")
def gateway_single(address: str):
    gateway = Gateway([address])
    asyncio.run(gateway.main())


@app.command()
def computer():
    computer = Computer()
    computer.gateway_subscriber.loop_forever()


@app.command()
def generate_csv(filename: Path):
    logger = Logger(filename)
    logger.computer_subscriber.loop_forever()


if __name__ == "__main__":
    app()
