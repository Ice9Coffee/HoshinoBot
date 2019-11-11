import os
from PIL import Image
from urllib.request import pathname2url
from urllib.parse import urljoin


from nonebot import get_bot
from nonebot import MessageSegment

class R:

    @staticmethod
    def get(path, *paths):
        return ResObj(os.path.join(path, *paths))

    @staticmethod
    def img(path, *paths):
        return ResImg(os.path.join('img', path, *paths))



class ResObj:

    def __init__(self, res_path):
        res_dir = get_bot().config.RESOURCE_DIR
        fullpath = os.path.abspath(os.path.join(res_dir, res_path))
        if not fullpath.startswith(os.path.abspath(res_dir)):
            raise ValueError('Cannot access outside RESOUCE_DIR')
        self.__path = os.path.normpath(res_path)


    @property
    def url(self):
        '''
        供酷Q使用
        '''
        if get_bot().config.RESOURCE_URL:
            return urljoin(get_bot().config.RESOURCE_URL, pathname2url(self.__path))
        else:
            return os.path.abspath(self.path)


    @property
    def path(self):
        '''
        供Nonebot内部使用
        '''
        res_dir = get_bot().config.RESOURCE_DIR
        return os.path.join(res_dir, self.__path)



class ResImg(ResObj):
    @property
    def cqcode(self) -> MessageSegment:
        return MessageSegment.image(self.url)

    def toPILImage(self) -> Image:
        return Image.open(self.path)
