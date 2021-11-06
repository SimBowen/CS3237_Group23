import asyncio
from typing import Callable

import arrow
from bleak import BleakClient
from up_goer.ahrs.ahrs import MadgwickAHRS, get_yaw
from up_goer.cc2650.cc2650 import (AccelerometerSensorMovementSensorMPU9250,
                                   GyroscopeSensorMovementSensorMPU9250,
                                   MagnetometerSensorMovementSensorMPU9250,
                                   MovementSensorMPU9250)
from up_goer.cfg import cfg
from up_goer.core.data_structures import MovementSensorData, SensorData


class Gateway:
    def __init__(self, tags: list):
        print(f"Initializing gateway with tags: {tags}")
        self.tags = tags
        self.ahrs_list = [
            MadgwickAHRS(cfg.SAMPLE_PERIOD, cfg.BETA) for _ in range(len(tags))
        ]

    async def output_data(
        self, functor: Callable[[[float, float, float]], None] = None
    ):
        while True:
            await asyncio.sleep(0.1)
            quaternions = [ahrs.quaternion for ahrs in self.ahrs_list]
            yaws = [get_yaw(*q) for q in quaternions]

            if yaws[0] == 0.0:
                continue
            functor(yaws)

    async def main(self, functor):
        await asyncio.gather(
            *[self.run(i) for i in range(len(self.tags))],
            self.output_data(functor),
        )

    async def run(self, tag_no):
        print(f"Connecting sensor: {tag_no}")
        async with BleakClient(self.tags[tag_no]) as client:
            x = await client.is_connected()
            print("Sensor " + str(tag_no) + " Connected: {0}".format(x))

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
                data = MovementSensorData(timestamp, gyro_data, acc_data, magneto_data)
                g, a, m = gyro_sensor.data, acc_sensor.data, magneto_sensor.data
                self.ahrs_list[tag_no].update(*g, *a, *m)
