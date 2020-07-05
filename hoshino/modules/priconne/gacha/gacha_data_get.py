# -*- coding: utf-8 -*-  #声明编码
import os, json, requests
#=====================================================================
#diy_gacha.json用于自定义卡池
#=====================================================================
class gacha_data(object):

    def __init__(self):
        self.set_gacha()

    def set_gacha(self):
        default_gacha = json.load(open(os.path.join(os.path.dirname(__file__),'config.json'), 'r'))#修一下或者整个指定目录
        self.__jp = default_gacha['JP']
        self.__cn = default_gacha['CN']
        self.__tw = default_gacha['TW']
        self.__all = default_gacha['ALL']
        if os.path.exists(os.path.join(os.path.dirname(__file__),'diy_gacha.json')):
            diy_gacha = json.load(open(os.path.join(os.path.dirname(__file__),'diy_gacha.json'), 'r'))
            self.__diy = diy_gacha    

    def get_jp(self):
        return self.__jp
    def get_cn(self):
        return self.__cn
    def get_tw(self):
        return self.__tw
    def get_all(self):
        return self.__all
    def get_diy(self):
        return self.__diy

def check_up():
    if os.path.exists(os.path.join(os.path.dirname(__file__),'gacha_ver.json')):
        with open(os.path.join(os.path.dirname(__file__),'gacha_ver.json'),'r') as lv:
            lvj = json.load(lv)
            loaclversion = int(lvj.get('ver', 0))
    else:
        loaclversion = 0

    load_ver = requests.get('https://api.redive.lolikon.icu/gacha/gacha_ver.json')#测试用的半自动更新卡池版本校对地址
    if load_ver.status_code != 200:
        return -1
    get_ver = int(load_ver.json().get('ver', 0))
    if get_ver <= loaclversion:
        return 0
    with open('gacha_ver.json','w') as lv :
        lv.write(load_ver.text)

    load_gacha = requests.get('https://api.redive.lolikon.icu/gacha/default_gacha.json')#测试用的半自动更新卡池地址
    if load_gacha.status_code != 200:
        return -1
    with open(os.path.join(os.path.dirname(__file__),'config.json'),'w') as gc:
        gc.write(load_gacha.text)
    gacha_data()


