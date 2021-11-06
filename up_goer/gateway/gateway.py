import asyncio

import arrow
from bleak import BleakClient
from up_goer.cc2650.cc2650 import (
    AccelerometerSensorMovementSensorMPU9250,
    GyroscopeSensorMovementSensorMPU9250,
    MagnetometerSensorMovementSensorMPU9250,
    MovementSensorMPU9250,
)
from up_goer.cfg import cfg
from up_goer.core.data_structures import SensorData, SensorTagData


class Gateway:
    def __init__(self, tags: list):
        print(f"Initializing gateway with tags: {tags}")
        # TODO: hacky way to pass data from while true loop
        self.sensor_tags = dict[str, SensorTagData or None]()
        for address in tags:
            self.sensor_tags[address] = None

    async def main(self, functor):
        await asyncio.gather(
            *[self.connect(i) for i in range(len(self.tags))],
            self.output_data(),
        )

    async def connect(self, address: str):
        print(f"Connecting sensor: {address}")
        async with BleakClient(address) as client:
            x = await client.is_connected()
            print("Sensor " + address + " Connected: {0}".format(x))

            acc_sensor = AccelerometerSensorMovementSensorMPU9250()
            gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
            magneto_sensor = MagnetometerSensorMovementSensorMPU9250()

            movement_sensor = MovementSensorMPU9250()
            movement_sensor.register(acc_sensor)
            movement_sensor.register(gyro_sensor)
            movement_sensor.register(magneto_sensor)
            await movement_sensor.start_listener(client)

            while True:
                await asyncio.sleep(0.1)
                timestamp = arrow.now("+08:00").timestamp()
                gyro_data = SensorData(*gyro_sensor.data)
                acc_data = SensorData(*acc_sensor.data)
                magneto_data = SensorData(*magneto_sensor.data)
                data = SensorTagData(
                    client.address, timestamp, gyro_data, acc_data, magneto_data
                )
                self.sensor_tags[client.address] = data

    async def output_data(self):
        while True:
            await asyncio.sleep(0.1)
            for address, data in self.sensor_tags.items():
                pass
            # TODO: Publish to mqtt
