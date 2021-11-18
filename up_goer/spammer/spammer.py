import os
from pathlib import Path

import arrow
from paho.mqtt.client import Client
from up_goer.cfg import cfg
from up_goer.core.data_structures import ClassifyingData, PredictingData

class Spammer:
	def __init__(self):
		self.server_subscriber = Client()
		self.server_subscriber.on_connect = self.on_connect
		self.server_subscriber.on_message = self.on_message
		self.server_subscriber.connect(cfg.HOST)

	def blast(self, path: Path):
		with open(path, "r") as file:
			for line in file:
				print(line)

	def on_connect(self, client: Client, userdata, flags, result_code):
		if client is not self.server_subscriber:
			return
		client.subscribe(cfg.PREDICT_TOPIC)

	def on_message(self, client: Client, userdata, message):
		if client is not self.server_subscriber:
			return
		if message.topic != cfg.PREDICT_TOPIC:
			return
		payload = message.payload.decode()
		data = PredictingData.from_json(payload)
		self._parse(data)

	def _parse(self, data: PredictingData):
		print(data.data)
