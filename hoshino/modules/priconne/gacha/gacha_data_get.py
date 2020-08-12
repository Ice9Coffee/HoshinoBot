# -*- coding: utf-8 -*-  #声明编码
import os, json, requests, asyncio, re

class gacha_data(object):

    def __init__(self):
        self.set_gacha()

    def set_gacha(self):
        default_gacha = json.load(open(os.path.join(os.path.dirname(__file__),'config.json'), 'r'))#修一下或者整个指定目录
        self._jp = default_gacha['JP']
        self._bl = default_gacha['BL']
        self._tw = default_gacha['TW']
        self._all = default_gacha['ALL']
        if os.path.exists(os.path.join(os.path.dirname(__file__),'diy_gacha.json')):
            diy_gacha = json.load(open(os.path.join(os.path.dirname(__file__),'diy_gacha.json'), 'r'))
            self.__diy = diy_gacha    

    def get_jp(self):
        return self._jp
    def get_bl(self):
        return self._bl
    def get_tw(self):
        return self._tw
    def get_all(self):
        return self._all
    def get_diy(self):
        return self._diy


def check_up():
    if os.path.exists(os.path.join(os.path.dirname(__file__),'gacha_ver.json')):
        with open(os.path.join(os.path.dirname(__file__),'gacha_ver.json'),'r') as lv:
            lvj = json.load(lv)
            loaclversion = int(lvj.get('ver', 0))
    else:
        loaclversion = 0

    load_ver = requests.get('https://api.redive.lolikon.icu/gacha/gacha_ver.json')#测试用的半自动更新卡池版本校对地址
    if load_ver.status_code != 200:
        return 
    get_ver = int(load_ver.json().get('ver', 0))
    if get_ver <= loaclversion:
        return 
    with open('gacha_ver.json','w') as lv :
        lv.write(load_ver.text)

    load_gacha = requests.get('https://api.redive.lolikon.icu/gacha/default_gacha.json')#测试用的半自动更新卡池地址
    if load_gacha.status_code != 200:
        return 
    with open(os.path.join(os.path.dirname(__file__),'config.json'),'w') as gc:
        gc.write(load_gacha.text)
    load_unitdata = requests.get('https://api.redive.lolikon.icu/gacha/unitdata.py')
    if load_unitdata.status_code != 200:
        return
    with open(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), '_pcr_data.py'), 'w', encoding='utf-8') as pd:#此更新会让本地自定义的别名失效
        _out = re.sub(r"\n","",load_unitdata.text)
        _load_data = f'''#公主连接Re:dive的角色昵称数据
#格式 id:[日服原名,(如果有/没有重复的) 台服译名繁体, B服译名, Ice-Cirno/hoshinobot/…/_pcr_data.py, 自定义昵称] (<-依此顺序)
{_out}'''
        pd.write(_load_data)
        return 'up'
