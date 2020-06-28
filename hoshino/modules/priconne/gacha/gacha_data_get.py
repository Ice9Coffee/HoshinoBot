# -*- coding: utf-8 -*-  #声明编码
import os, json, requests
#=====================================================================
#diy_gacha.json用于自定义卡池
#=====================================================================
class gacha_data(object):#卡池
	jp = {}
	cn = {}
	tw = {}
	all = {}
	diy = {}
_gd = gacha_data()
class get_gacha(object):#检查更新数据
	
	def __init__(self):
		self.check_up()
		self.set_gacha()

	def check_up(self):
		if os.path.exists('gacha_ver.json'):
			with open('gacha_ver.json','r') as lv:
				lvj = json.load(lv)
				loaclversion = int(lvj.get('ver', 0))
		else:
			loaclversion = 0
		load_ver = requests.get('https://lolicon.plus/gacha/gacha_ver.json')#演示用的线上verjson
		if load_ver.status_code != 200:
			return -1
		get_ver = int(load_ver.json().get('ver', 0))
		if get_ver <= loaclversion:
			return 0
		with open('gacha_ver.json','w') as lv :
			lv.write(load_ver.text)
		load_gacha = requests.get('https://lolicon.plus/gacha/default_gacha.json')#演示用的线上gachajson
		if load_gacha.status_code != 200:
			return -1
		with open('default_gacha.json','w') as gc:
			gc.write(load_gacha.text)

	def set_gacha(self):
		default_gacha = json.load(open('default_gacha.json', 'r'))
		_gd.jp = default_gacha['jp']
		_gd.cn = default_gacha['cn']
		_gd.tw = default_gacha['tw']
		_gd.all = default_gacha['all']
		if os.path.exists('diy_gacha.json'):
			diy_gacha = json.load(open('diy_gacha.json', 'r'))
			_gd.diy = diy_gacha

get_gacha()
print(f'{_gd.jp}\n{_gd.cn}\n{_gd.tw}\n{_gd.all}\n{_gd.diy}')
