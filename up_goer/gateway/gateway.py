import asyncio
import json
import uuid
from typing import Callable

from bleak import BleakClient
from paho.mqtt.client import Client

from up_goer.cfg import cfg
from up_goer.ahrs.ahrs import MadgwickAHRS, get_yaw
from up_goer.cc2650.cc2650 import (
    AccelerometerSensorMovementSensorMPU9250,
    GyroscopeSensorMovementSensorMPU9250,
    MagnetometerSensorMovementSensorMPU9250,
    MovementSensorMPU9250,
)


class Gateway:
    def __init__(self, client: Client, tags: list):
        print(f"Initializing gateway with tags: {tags}")
        self.client = client
        self.tags = tags
        self.ahrs_list = [MadgwickAHRS(cfg.SAMPLE_PERIOD, cfg.BETA) for _ in range(len(tags))]

    async def output_data(
        self, functor: Callable[[[float, float, float]], None] = None
    ):
        while True:
            await asyncio.sleep(0.1)
            yaws = [get_yaw(*ahrs.quaternion) for ahrs in self.ahrs_list]

            if yaws[0] == 0.:
                continue

            data = {"id": str(uuid.uuid4()), "data": yaws}
            self.client.publish(cfg.CLASSIFY_TOPIC, json.dumps(data))
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
            print(f"Sensor {tag_no} Connected: {x}")

            sub_sensors = [
                AccelerometerSensorMovementSensorMPU9250(),
                GyroscopeSensorMovementSensorMPU9250(),
                MagnetometerSensorMovementSensorMPU9250(),
            ]
            movement_sensor = MovementSensorMPU9250()
            for sub_sensor in sub_sensors:
                movement_sensor.register(sub_sensor)
            await movement_sensor.start_listener(client)

            while True:
                await asyncio.sleep(0.1)
                gam = [i for s in sub_sensors for i in s.data]
                self.ahrs_list[tag_no].update(*gam)
