import os
from PIL import Image
from urllib.request import pathname2url
from urllib.parse import urljoin

from nonebot import get_bot
from nonebot import MessageSegment

from hoshino.util import pic2b64
from hoshino import logger

class R:

    @staticmethod
    def get(path, *paths):
        return ResObj(os.path.join(path, *paths))

    @staticmethod
    def img(path, *paths):
        return ResImg(os.path.join('img', path, *paths))



class ResObj:

    def __init__(self, res_path):
        res_dir = os.path.expanduser(get_bot().config.RESOURCE_DIR)
        fullpath = os.path.abspath(os.path.join(res_dir, res_path))
        if not fullpath.startswith(os.path.abspath(res_dir)):
            raise ValueError('Cannot access outside RESOUCE_DIR')
        self.__path = os.path.normpath(res_path)


    @property
    def url(self):
        """
        @return: 资源文件的url，供酷Q（或其他远程服务）使用
        """
        return urljoin(get_bot().config.RESOURCE_URL, pathname2url(self.__path))


    @property
    def path(self):
        """
        @return: 资源文件的路径，供Nonebot内部使用
        """
        res_dir = os.path.expanduser(get_bot().config.RESOURCE_DIR)
        return os.path.join(res_dir, self.__path)


    @property
    def exist(self):
        return os.path.exists(self.path)


class ResImg(ResObj):
    @property
    def cqcode(self) -> MessageSegment:
        if get_bot().config.RESOURCE_URL:
            return MessageSegment.image(self.url)
        else:
            try:
                return MessageSegment.image(pic2b64(self.open()))
            except Exception as e:
                logger.exception(e)
                return MessageSegment.text('[图片]')

    def open(self) -> Image:
        return Image.open(self.path)
