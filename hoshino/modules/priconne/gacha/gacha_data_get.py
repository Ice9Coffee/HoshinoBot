# -*- coding: utf-8 -*-  #声明编码
import os, json, requests
#=====================================================================
#diy_gacha.json用于自定义卡池
#=====================================================================
class gacha_data(object):

	def __init__(self):
		self.set_gacha()

	def set_gacha(self):
		default_gacha = json.load(open('default_gacha.json', 'r'))
		self.__jp = default_gacha['jp']
		self.__cn = default_gacha['cn']
		self.__tw = default_gacha['tw']
		self.__all = default_gacha['all']
		if os.path.exists('diy_gacha.json'):
			diy_gacha = json.load(open('diy_gacha.json', 'r'))
			self.__diy = diy_gacha	

	#用于调用预存的抽卡列表?
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


class get_gacha(object):#检查更新数据
	
	def __init__(self):
		self.check_up()

	def check_up(self):
		if os.path.exists('gacha_ver.json'):
			with open('gacha_ver.json','r') as lv:
				lvj = json.load(lv)
				loaclversion = int(lvj.get('ver', 0))
		else:
			loaclversion = 0

		load_ver = requests.get('https://api.redive.lolikon.icu/gacha/gacha_ver.json')
		if load_ver.status_code != 200:
			return -1
		get_ver = int(load_ver.json().get('ver', 0))
		if get_ver <= loaclversion:
			return 0
		with open('gacha_ver.json','w') as lv :
			lv.write(load_ver.text)

		load_gacha = requests.get('https://api.redive.lolikon.icu/gacha/default_gacha.json')
		if load_gacha.status_code != 200:
			return -1
		with open('default_gacha.json','w') as gc:
			gc.write(load_gacha.text)
