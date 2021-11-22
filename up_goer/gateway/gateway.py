import asyncio

import arrow
import click
from bleak import BleakClient
from paho.mqtt.client import Client
from up_goer.cc2650.cc2650 import (
    AccelerometerSensorMovementSensorMPU9250,
    GyroscopeSensorMovementSensorMPU9250,
    MagnetometerSensorMovementSensorMPU9250,
    MovementSensorMPU9250,
)
from up_goer.cfg import cfg
from up_goer.core.data_structures import GatewayData, SensorData, SensorTagData


class Gateway:
    def __init__(self, sensor_tags: list):
        print(f"Initializing gateway with tags: {sensor_tags}")
        # TODO: hacky way to pass data from while true loop
        self.sensor_tags = dict[str, SensorTagData or None]()
        for address in sensor_tags:
            self.sensor_tags[address] = None

        self.computer_publisher = Client()
        self.computer_publisher.connect(cfg.COMPUTER_HOST)

    async def main(self):
        await asyncio.gather(
            *[self.connect(address) for address in self.sensor_tags.keys()],
            self.output_data(),
        )

    async def connect(self, address: str):
        print(f"Connecting sensor: {address}")
        async with BleakClient(address) as client:
            x = await client.is_connected()
            click.echo(f"Sensor {address} Connected: {x}")

            acc_sensor = AccelerometerSensorMovementSensorMPU9250()
            gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
            magneto_sensor = MagnetometerSensorMovementSensorMPU9250()

            movement_sensor = MovementSensorMPU9250()
            movement_sensor.register(acc_sensor)
            movement_sensor.register(gyro_sensor)
            movement_sensor.register(magneto_sensor)
            await movement_sensor.start_listener(client)

            init = False
            while True:
                await asyncio.sleep(0.1)
                if not await client.is_connected():
                    raise ConnectionError()
                timestamp = arrow.now("+08:00").timestamp()
                gyro_data = SensorData(*gyro_sensor.data)
                acc_data = SensorData(*acc_sensor.data)
                magneto_data = SensorData(*magneto_sensor.data)
                data = SensorTagData(
                    client.address, timestamp, gyro_data, acc_data, magneto_data
                )

                # Check for initial invalid data
                if not init:
                    if not data.is_valid():
                        continue
                    init = True

                self.sensor_tags[client.address] = data

    async def output_data(self):
        while True:
            await asyncio.sleep(0.1)
            if None in self.sensor_tags.values():
                continue
            payload = GatewayData(list(self.sensor_tags.values()))
            payload = payload.to_json().encode()
            self.computer_publisher.publish(cfg.GATEWAY_TOPIC, payload=payload)
