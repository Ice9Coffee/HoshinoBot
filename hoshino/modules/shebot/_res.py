import os
import re
from io import BytesIO
from os import path
from typing import Union

import nonebot
from aiocqhttp.event import Event
from aiocqhttp.message import Message
from filetype.filetype import guess_mime
from PIL import Image
from nonebot.message import MessageSegment

from ._util import download_async, get_md5, get_random_file, logger, bot


class Res:
    base_dir = path.join(path.dirname(__file__), 'res')
    image_dir = path.join(base_dir, 'image')
    record_dir = path.join(base_dir, 'record')
    img_cache_dir = path.join(image_dir, 'cache')

    def check_exist(res_path: str) -> None:
        return path.exists(res_path)

    @classmethod
    def image(cls, pic_path: str) -> 'MessageSegment':
        if cls.check_exist(pic_path):
            return MessageSegment.image(f'file:///{pic_path}')
        elif cls.check_exist(path.join(cls.image_dir, pic_path)):
            return MessageSegment.image(f'file:///{path.join(cls.image_dir, pic_path)}')
        else:
            return '【图片丢了】'

    @classmethod
    def record(cls, rec_path) -> 'MessageSegment':
        if cls.check_exist(rec_path):
            return MessageSegment.record(f'file:///{rec_path}')
        elif cls.check_exist(path.join(cls.record_dir, rec_path)):
            return MessageSegment.record(f'file:///{path.join(cls.record_dir, rec_path)}')
        else:
            return '【图片丢了】'

    @classmethod
    def cardimage(cls, pic_path: str) -> 'MessageSegment':
        if cls.check_exist(pic_path):
            return f"[CQ:cardimage,file=file:///{pic_path}]"
        elif cls.check_exist(path.join(cls.image_dir, pic_path)):
            return f"[CQ:cardimage,file=file:///{path.join(cls.image_dir, pic_path)}]"
        else:
            return '【图片丢了】'

    @classmethod
    def get_random_image(cls, folder=None) -> 'MessageSegment':
        if not folder:
            image_path = cls.image_dir
        else:
            image_path = path.join(cls.image_dir, folder)
        image_name = get_random_file(image_path)
        return cls.image(path.join(image_path, image_name))

    @classmethod
    def get_random_record(cls, folder=None) -> 'MessageSegment':
        if not folder:
            record_path = cls.record_dir
        else:
            record_path = path.join(cls.record_dir, folder)
        rec_name = get_random_file(record_path)
        return cls.record(path.join(record_path, rec_name))

    @classmethod
    async def image_from_url(cls, url: str, cache=True) -> 'MessageSegment':
        fname = get_md5(url)
        image = path.join(cls.img_cache_dir, f'{fname}.jpg')
        if not path.exists(image) or not cache:
            image = await download_async(url, cls.img_cache_dir, f'{fname}.jpg')
        return cls.image(image)

    @classmethod
    async def cardimage_from_url(cls, url: str, cache=True) -> 'MessageSegment':
        fname = get_md5(url)
        image = path.join(cls.img_cache_dir, f'{fname}.jpg')
        if not path.exists(image) or not cache:
            image = await download_async(url, cls.img_cache_dir, f'{fname}.jpg')
        return cls.cardimage(image)

    @classmethod
    def image_from_memory(cls, data: Union[bytes, Image.Image]) -> 'MessageSegment':
        if isinstance(data, Image.Image):
            out = BytesIO()
            data.save(out, format='png')
            data = out.getvalue()
        if not isinstance(data, bytes):
            raise ValueError('不支持的参数类型')
        ftype = guess_mime(data)
        if not ftype or not ftype.startswith('image'):
            raise ValueError('不是有效的图片类型')
        fn = get_md5(data)
        save_path = path.join(cls.img_cache_dir, fn)
        with open(save_path, 'wb') as f:
            f.write(data)
        return cls.image(path.join(cls.img_cache_dir, fn))
