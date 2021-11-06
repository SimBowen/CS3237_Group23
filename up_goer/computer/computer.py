from paho.mqtt.client import Client
from up_goer.ahrs.ahrs import MadgwickAHRS, get_yaw
from up_goer.cfg import cfg
from up_goer.core.data_structures import ClassifyingData, GatewayData


class Computer:
    def __init__(self):
        self.sensor_tag_dict: dict[str, MadgwickAHRS] = dict()
        self.gateway_subscriber = Client()
        self.gateway_subscriber.on_connect = self.on_connect
        self.gateway_subscriber.on_message = self.on_message
        self.gateway_subscriber.connect(cfg.GATEWAY_HOST)

        self.model_publisher = Client()
        self.model_publisher.username_pw_set(cfg.USER, cfg.PASSWORD)
        self.model_publisher.connect(cfg.HOST)

    def on_connect(self, client: Client, userdata, flags, result_code):
        client.subscribe(cfg.GATEWAY_TOPIC)

    def on_message(self, client: Client, userdata, message):
        if message.topic != cfg.GATEWAY_TOPIC:
            return
        payload = message.payload.decode()
        data = GatewayData.from_json(payload)
        for data in data.sensor_tags:
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

            payload = ClassifyingData(yaws).to_json().encode()
            self.model_publisher.publish(cfg.CLASSIFY_TOPIC, payload)
