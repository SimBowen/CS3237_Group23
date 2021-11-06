from paho.mqtt.client import Client
from up_goer.ahrs.ahrs import MadgwickAHRS, get_yaw
from up_goer.cfg import cfg
from up_goer.core.data_structures import SensorTagData


class Computer:
    def __init__(self):
        self.sensor_tag_dict: dict[str, MadgwickAHRS] = dict()
        self.sensor_client = Client()

    def on_connect(self, client: Client, userdata, flags, result_code):
        client.subscribe(cfg.SENSOR_TOPIC)

    def on_message(self, client: Client, userdata, message):
        if message.topic != cfg.SENSOR_TOPIC:
            return
        payload = message.payload.decode()
        data = SensorTagData.from_json(payload)
        if data.address not in self.sensor_tag_dict:
            self.sensor_tag_dict[data.address] = MadgwickAHRS(
                cfg.SAMPLE_PERIOD, cfg.BETA
            )
        sensor_tag = self.sensor_tag_dict.get(data.address)
        sensor_tag.update(*data.gyroscope, *data.accelerometer, *data.magnetometer)

        # dicts in python preserve insertion order
        quaternions = [
            ahrs.quaternion for address, ahrs in self.sensor_tag_dict.items()
        ]
        yaws = [get_yaw(*q) for q in quaternions]

        # TODO: Why skip first yaw?
        if yaws[0] == 0.0:
            return

        # TODO: Publish yaws to mqtt
