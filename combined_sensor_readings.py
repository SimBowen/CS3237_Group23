# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import csv
import math
import platform
import struct
import time

from bleak import BleakClient

LABEL = "1"
READY = -1


class Service:
    """
    Here is a good documentation about the concepts in ble;
    https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt

    In TI SensorTag there is a control characteristic and a data characteristic which define a service or sensor
    like the Light Sensor, Humidity Sensor etc

    Please take a look at the official TI user guide as well at
    https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
    """

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None


class Sensor(Service):
    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def start_listener(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)


class MovementSensorMPU9250SubService:
    def __init__(self):
        self.bits = 0

    def enable_bits(self):
        return self.bits

    def cb_sensor(self, data):
        raise NotImplementedError


class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G = 0 << 8
    ACCEL_RANGE_4G = 1 << 8
    ACCEL_RANGE_8G = 2 << 8
    ACCEL_RANGE_16G = 3 << 8
    scaleA = 8.0 / 32768.0  # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def __init__(self, address):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.ctrlBits = 0
        self.add = address
        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    async def start_listener(self, client, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

    async def onDemand(self, client, posture, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))
        # listen using the handler
        await asyncio.sleep(1.5)
        data = await client.read_gatt_char(self.data_uuid)
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        rawA = unpacked_data[3:6]
        accel = tuple([v * self.scaleA for v in rawA])
        pitch = (
            180
            * math.atan(accel[0] / math.sqrt(accel[1] * accel[1] + accel[2] * accel[2]))
            / math.pi
        )
        roll = (
            180
            * math.atan(accel[2] / math.sqrt(accel[1] * accel[1] + accel[2] * accel[2]))
            / math.pi
        )
        yaw = (
            180
            * math.atan(accel[0] / math.sqrt(accel[0] * accel[0] + accel[2] * accel[2]))
            / math.pi
        )
        print(
            "roll: {roll}, pitch: {pitch}, yaw: {yaw}".format(
                roll=roll, pitch=pitch, yaw=yaw
            )
        )
        """ with open('rpy.csv', 'w', newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            wr.writerow([time.strftime("%H:%M:%S"), self.add, posture, roll, pitch, yaw]) """

        # await asyncio.sleep(1.0)
        # await client.disconnect()
        # await client.start_notify(self.data_uuid, self.callback)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data)


class AllMovementSensorsMPU9250(MovementSensorMPU9250SubService):
    def __init__(self, address):
        super().__init__()
        self.bits = (
            MovementSensorMPU9250.ACCEL_XYZ
            | MovementSensorMPU9250.ACCEL_RANGE_4G
            | MovementSensorMPU9250.MAG_XYZ
            | MovementSensorMPU9250.GYRO_XYZ
        )
        self.scaleA = (
            8.0 / 32768.0
        )  # TODO: why not 4.0, as documented? @Ashwin Need to verify
        self.scaleM = 4912.0 / 32760
        self.scaleG = 500.0 / 65536.0
        self.add = address
        self.pitch = 0

    def cb_sensor(self, data):
        """Returns (x_accel, y_accel, z_accel) in units of g"""
        rawG = data[0:3]
        rawA = data[3:6]
        rawM = data[6:9]
        global READY
        READY += 1
        if READY == 0:
            print("Setup not ready, please wait...")
        elif READY == 1:
            print("Setup ready, please do your action...")
        elif READY >= 2:
            accel = tuple([v * self.scaleA for v in rawA])
            pitch = (
                180
                * math.atan(
                    accel[0] / math.sqrt(accel[1] * accel[1] + accel[2] * accel[2])
                )
                / math.pi
            )
            roll = (
                180
                * math.atan(
                    accel[2] / math.sqrt(accel[1] * accel[1] + accel[2] * accel[2])
                )
                / math.pi
            )
            yaw = (
                180
                * math.atan(
                    accel[0] / math.sqrt(accel[0] * accel[0] + accel[2] * accel[2])
                )
                / math.pi
            )
            # print("[{add}] roll: {roll}, pitch: {pitch}, yaw: {yaw}".format(add = self.add, roll = roll, pitch = pitch, yaw = yaw))
            self.pitch = pitch
            # Add code for MQTT here


"""             with open('rpy.csv', 'w', newline='') as csvfile:
                wr = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                wr.writerow([time.strftime("%H:%M:%S"), self.add, roll, pitch, yaw]) """


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = (
            MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        )
        self.scale = (
            8.0 / 32768.0
        )  # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def cb_sensor(self, data):
        """Returns (x_accel, y_accel, z_accel) in units of g"""
        rawVals = data[3:6]
        global READY
        READY += 1
        if READY == 0:
            print("Setup not ready, please wait...")
        elif READY == 1:
            print("Setup ready, please do your action...")
        elif READY >= 2:
            # with open('./train/IndividualSignals/acc_x_train.csv','a') as a, \
            #      open('./train/IndividualSignals/acc_y_train.csv','a') as b, \
            #      open('./train/IndividualSignals/acc_z_train.csv','a') as c:
            #     a.write("{}\n".format(rawVals[0]))
            #     b.write("{}\n".format(rawVals[1]))
            #     c.write("{}\n".format(rawVals[2]))
            # wr = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            # wr.writerow(str(rawVals))
            print(
                time.strftime("%H:%M:%S"),
                "[MovementSensor] Accelerometer:",
                tuple([v * self.scale for v in rawVals]),
            )


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760
        # Reference: MPU-9250 register map v1.4

    def cb_sensor(self, data):
        """Returns (x_mag, y_mag, z_mag) in units of uT"""
        rawVals = data[6:9]
        global READY

        if READY >= 2:
            # with open('./train/IndividualSignals/mag_x_train.csv','a') as a, \
            #      open('./train/IndividualSignals/mag_y_train.csv','a') as b, \
            #      open('./train/IndividualSignals/mag_z_train.csv','a') as c:
            #     a.write("{}\n".format(rawVals[0]))
            #     b.write("{}\n".format(rawVals[1]))
            #     c.write("{}\n".format(rawVals[2]))
            print(
                "[MovementSensor] Magnetometer:",
                tuple([v * self.scale for v in rawVals]),
            )


class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0 / 65536.0

    def cb_sensor(self, data):
        """Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec"""
        rawVals = data[0:3]
        global READY
        if READY >= 2:
            # with open('./train/IndividualSignals/gyro_x_train.csv','a') as a, \
            #      open('./train/IndividualSignals/gyro_y_train.csv','a') as b, \
            #      open('./train/IndividualSignals/gyro_z_train.csv','a') as c:
            #     a.write("{}\n".format(rawVals[0]))
            #     b.write("{}\n".format(rawVals[1]))
            #     c.write("{}\n".format(rawVals[2]))
            print(
                "[MovementSensor] Gyroscope:", tuple([v * self.scale for v in rawVals])
            )


class LEDAndBuzzer(Service):
    """
    Adapted from various sources. Src: https://evothings.com/forum/viewtopic.php?t=1514 and the original TI spec
    from https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Activating_IO

    Codes:
        1 = red
        2 = green
        3 = red + green
        4 = buzzer
        5 = red + buzzer
        6 = green + buzzer
        7 = all
    """

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa65-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa66-0451-4000-b000-000000000000"

    async def notify(self, client, code):
        # enable the config
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # turn on the red led as stated from the list above using 0x01
        write_value = bytearray([code])
        await client.write_gatt_char(self.data_uuid, write_value)


async def connectBLE(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        return client


async def take_reading(address, posture):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))
        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        movement_sensor = MovementSensorMPU9250(address)
        movement_sensor.register(acc_sensor)
        await movement_sensor.onDemand(client, posture)


Acc1 = AllMovementSensorsMPU9250("54:6C:0E:52:F3:D1")
movement_sensor1 = MovementSensorMPU9250("54:6C:0E:52:F3:D1")
movement_sensor1.register(Acc1)

Acc2 = AllMovementSensorsMPU9250("Address2")
movement_sensor2 = MovementSensorMPU9250("Address2")
movement_sensor2.register(Acc2)

Acc3 = AllMovementSensorsMPU9250("Address3")
movement_sensor3 = MovementSensorMPU9250("Address3")
movement_sensor3.register(Acc3)


async def run_1(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Sensor 1 Connected: {0}".format(x))
        await movement_sensor1.start_listener(client)
        while True:
            # we don't want to exit the "with" block initiating the client object
            # as the connection is disconnected unless the object is stored
            await asyncio.sleep(0.1)


async def run_2(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Sensor 2 Connected: {0}".format(x))
        await movement_sensor2.start_listener(client)
        while True:
            # we don't want to exit the "with" block initiating the client object
            # as the connection is disconnected unless the object is stored
            await asyncio.sleep(0.1)


async def run_3(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Sensor 3 Connected: {0}".format(x))
        await movement_sensor3.start_listener(client)
        cntr = 0

        while True:
            # we don't want to exit the "with" block initiating the client object
            # as the connection is disconnected unless the object is stored
            await asyncio.sleep(0.1)


async def print_value(sensor1, sensor2, sensor3):
    while True:
        print(
            f"pitch_1: {sensor1.pitch}, pitch_2: {sensor2.pitch}, pitch_3: {sensor3.pitch}"
        )
        await asyncio.sleep(1)
        # Can mqtt from here, values are sensor1.pitch, sensor2.pitch and sensor3.pitch


async def main():
    print("Setting up. First values are garbage values.")
    await asyncio.gather(run_1("54:6C:0E:52:F3:D1"), print_value(Acc1, Acc2, Acc3))
    # run the bottom function instead for multile sensors
    # await asyncio.gather(run_1("54:6C:0E:52:F3:D1"),run_2("Address2"), run_3("Address3"), print_value(Acc1,Acc2,Acc3))


if __name__ == "__main__":
    asyncio.run(main())
