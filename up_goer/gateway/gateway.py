import asyncio
from typing import Callable

from bleak import BleakClient
from up_goer.ahrs.ahrs import MadgwickAHRS, get_yaw
from up_goer.cc2650.cc2650 import (
    AccelerometerSensorMovementSensorMPU9250,
    GyroscopeSensorMovementSensorMPU9250,
    MagnetometerSensorMovementSensorMPU9250,
    MovementSensorMPU9250,
)


class Gateway:
    def __init__(self):
        self.ahrs1 = MadgwickAHRS(1 / 10, 3)
        self.ahrs2 = MadgwickAHRS(1 / 10, 3)
        self.ahrs3 = MadgwickAHRS(1 / 10, 3)

    async def output_data(
        self, functor: Callable[[[float, float, float]], None] = None
    ):
        while True:
            await asyncio.sleep(0.1)
            yaw_1 = get_yaw(*self.ahrs1.quaternion)
            yaw_2 = get_yaw(*self.ahrs2.quaternion)
            yaw_3 = get_yaw(*self.ahrs3.quaternion)

            if yaw_1 == 0.00:
                continue
            # save_data(yaw_1,yaw_2,yaw_3)
            print([yaw_1, yaw_2, yaw_3])
            functor([yaw_1, yaw_2, yaw_3])

    async def main(self, functor):
        await asyncio.gather(
            self.run("54:6C:0E:52:F3:D1", 1),
            self.run("54:6C:0E:53:37:DA", 2),
            self.run("54:6C:0E:53:37:44", 3),
            self.output_data(functor),
        )

    async def run(self, address, tag):
        async with BleakClient(address) as client:
            x = await client.is_connected()
            print("Sensor " + str(tag) + " Connected: {0}".format(x))

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
                g, a, m = gyro_sensor.data, acc_sensor.data, magneto_sensor.data
                if tag == 1:
                    self.ahrs1.update(*g, *a, *m)
                elif tag == 2:
                    self.ahrs2.update(*g, *a, *m)
                elif tag == 3:
                    self.ahrs3.update(*g, *a, *m)
