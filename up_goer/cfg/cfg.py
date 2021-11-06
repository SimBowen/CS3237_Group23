from dotenv import dotenv_values

from up_goer.utils.utils import get_tag_address

HOST = "xinming.ddns.net"
USER = "guest"
PASSWORD = dotenv_values()["SERVER_PASSWORD"]
PREDICT_TOPIC = "posture/predict"
CLASSIFY_TOPIC = "posture/classify"

TAG_ADDRESS_1 = get_tag_address("54:6C:0E:52:F3:D1", "54FCFF89-ED9C-4C6A-9FD8-58AB675D5992")
TAG_ADDRESS_2 = get_tag_address("54:6C:0E:53:37:44", "22B9C408-07FF-41EC-9C28-21EC34AFD42E")
TAG_ADDRESS_3 = get_tag_address("54:6C:0E:53:37:DA", "BBC05C31-1B99-4567-90DF-9CA8412F4670")
TAG_ADDRESS_4 = get_tag_address("98:07:2D:1D:50:86", "86ECDCBA-A097-4061-BE0E-65AB0CFA049C")

SAMPLE_PERIOD = 1 / 10
BETA = 2.5
