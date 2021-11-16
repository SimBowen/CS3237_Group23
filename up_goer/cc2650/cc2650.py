# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import math
import struct


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

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.rate_uuid = "f000aa83-0451-4000-b000-000000000000"
        self.ctrlBits = 0
        self.rate = 0x0A

        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    async def start_listener(self, client, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))
        await client.write_gatt_char(self.rate_uuid, struct.pack("<H", self.rate))

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data)


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = (
            MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        )
        self.scale = (
            8.0 / 32768.0
        )  # TODO: why not 4.0, as documented? @Ashwin Need to verify
        self.data = [0, 0, 0]

    def cb_sensor(self, data):
        """Returns (x_accel, y_accel, z_accel) in units of g"""
        rawVals = data[3:6]
        scaled_data = tuple([v * self.scale for v in rawVals])
        self.data[0] = scaled_data[0]
        self.data[1] = scaled_data[1]
        self.data[2] = scaled_data[2]
        # print("[MovementSensor] Accelerometer:", tuple([ v*self.scale for v in rawVals ]))


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760
        # Reference: MPU-9250 register map v1.4
        self.data = [0, 0, 0]

    def cb_sensor(self, data):
        """Returns (x_mag, y_mag, z_mag) in units of uT"""
        rawVals = data[6:9]
        scaled_data = tuple([v * self.scale for v in rawVals])
        self.data[0] = scaled_data[0]
        self.data[1] = scaled_data[1]
        self.data[2] = scaled_data[2]
        # print("[MovementSensor] Magnetometer:", scaled_data)


class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0 / 65536.0
        self.data = [0, 0, 0]

    def cb_sensor(self, data):
        """Returns (x_gyro, y_gyro, z_gyro) in units of rad/sec"""
        rawVals = data[0:3]
        scaled_data = tuple([v * self.scale * math.pi / 180 for v in rawVals])

        self.data[0] = scaled_data[0]
        self.data[1] = scaled_data[1]
        self.data[2] = scaled_data[2]
        # print("[MovementSensor] Gyroscope:", scaled_data)
