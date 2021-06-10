import json
import requests
from datetime import datetime, timedelta
from math import sqrt
from os import path, listdir
from random import choice, randint, shuffle

import aiohttp
from PIL import Image

from .config import CLIENT_ID, CLIENT_SECRET
from .._util import load_config
from .._res import Res as R


class KyaruHead:
    def __init__(self, head_name, angle, face_width, chin_tip_x, chin_tip_y, cqcode) -> None:
        self.head_name = head_name
        self.angle = angle
        self.face_width = face_width
        self.X = chin_tip_x
        self.Y = chin_tip_y
        self.cqcode = cqcode

    @property
    def img(self):
        head = path.join(path.dirname(__file__), 'data/head', self.head_name, f'{self.head_name}.png')
        return Image.open(head)

    @classmethod
    def from_name(cls, head_name):
        dat_path = path.join(path.dirname(__file__), 'data/head', head_name, 'dat.json')
        pic_path = path.join(path.dirname(__file__), 'data/head', head_name, f'{head_name}.png')
        dat = load_config(dat_path)
        cqcode = R.image(pic_path)
        return cls(head_name, dat['angle'], dat['face_width'], dat['chin_tip_x'], dat['chin_tip_y'], cqcode)

    @staticmethod
    def exist_head(head_name):
        if not path.exists(path.join(path.dirname(__file__), 'data/head', head_name)):
            return False
        if not path.exists(path.join(path.dirname(__file__), 'data/head', head_name, f'{head_name}.png')):
            return False
        return True

    @classmethod
    def rand_head(cls):
        heads = []
        for i in listdir(path.join(path.dirname(__file__), 'data/head')):
            if path.isdir(path.join(path.dirname(__file__), 'data/head', i)):
                heads.append(i)
        return cls.from_name(choice(heads))


def auto_head(face_dat: dict) -> KyaruHead:
    # TODO
    return KyaruHead.from_name(str(randint(1, 3)))


def gen_head():
    heads = []
    for i in listdir(path.join(path.dirname(__file__), 'data/head')):
        if path.isdir(path.join(path.dirname(__file__), 'data/head', i)):
            heads.append(i)
    shuffle(heads)
    for head in heads:
        yield KyaruHead.from_name(head)


def get_token() -> str:
    grant_type = 'client_credentials'
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {'grant_type': grant_type, 'client_id': client_id, 'client_secret': client_secret}
    with requests.get(url, params) as resp:
        data = resp.json()
        token = data['access_token']
        expire_time = datetime.now() + timedelta(seconds=data['expires_in'])
        return token, expire_time


async def detect_face(imgb64: str) -> dict:
    token = get_token()
    api_url = f'https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={token[0]}'
    data = {
        "image": imgb64,
        "image_type": "BASE64",
        "face_field": "face_type,eye_status,landmark",
        "max_face_num": 3
    }
    async with  aiohttp.ClientSession() as session:
        async with session.post(api_url, data=data) as resp:
            text = await resp.text()
            data = json.loads(text)
            if data['error_msg'] == 'SUCCESS':
                face_data_list = []
                for face in data['result']['face_list']:
                    left = face['location']['left']
                    top = face['location']['top']
                    location = (left, top, left + face['location']['width'], top + face['location']['height'])
                    l_eye_pos = face['landmark'][0]['x'], face['landmark'][0]['y']
                    r_eye_pos = face['landmark'][1]['x'], face['landmark'][1]['y']
                    face_data_list.append({
                        "location": location,
                        "left_eye": l_eye_pos,
                        "right_eye": r_eye_pos,
                        "rotation": face['location']['rotation'],
                        "landmark72": face['landmark72']
                    })
                return face_data_list
            else:
                return None


def distance_between_point(p1, p2):
    if isinstance(p1, dict):
        p1 = (p1['x'], p1['y'])
    if isinstance(p2, dict):
        p2 = (p2['x'], p2['y'])
    return sqrt((p1[0] - p2[0]) ** 2 + (p2[1] - p2[1]) ** 2)


def concat(img: Image.Image, head: KyaruHead, face_dat) -> Image.Image:
    lm = face_dat['landmark72']
    scale = distance_between_point(lm[0], lm[12]) / head.face_width / 0.97  # 设置缩放， 0.97为系数，无实际意义
    w, h = head.img.size
    head_img = head.img.resize((int(scale * w), int(scale * h)), Image.BILINEAR)
    head_img = head_img.rotate(-face_dat['rotation'] - head.angle, center=(head.X * scale, head.Y * scale),
                               resample=Image.BILINEAR)
    img.paste(head_img, (int(lm[6]['x'] - head.X * scale), int(lm[6]['y'] - head.Y * scale)), mask=head_img.split()[3])
    return img
