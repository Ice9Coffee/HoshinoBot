import time
import requests
import re
import ujson as json
import pandas as pd
import numpy as np
from os import path
from datetime import datetime

from logging import getLogger

from ..util import CharaHelper

class Arena(object):

    @staticmethod
    def get_auth_key():
        config_file = path.join(path.dirname(__file__), "config.json")
        with open(config_file) as f:
            config = json.load(f)
            return config["AUTH_KEY"]

    @staticmethod
    def do_query(id_list):
        print(f'[{datetime.now()} Arena.do_query] id_list={id_list}')
        header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                'authorization':Arena.get_auth_key()}
        payload = {"_sign":"a", "def":id_list, "nonce":"a", "page":1, "sort":1, "ts": int(time.time())}
        print(f'[{datetime.now()} Arena.do_query] payload={json.dumps(payload)}')
        
        resp = requests.post('https://api.pcrdfans.com/x/v1/search', headers=header, data=json.dumps(payload))
        res = resp.json()
        # print(type(res))
        # print(res)
        print(f'[{datetime.now()} Arena.do_query] len(res)=', len(res))
        res = res['data']['result']
        res = [ [ (c['id'] // 100, c['star'], c['equip']) for c in x['atk'] ] for x in res ]
        return res

    # name>>>id
    @staticmethod
    def user_input(name_list):
        '''
        :param name_list: List[角色名], 可用别称

        return: id_list: List[int], str(角色id) + '01'
        '''
        return [ (CharaHelper.get_id(name) * 100 + 1)  for name in name_list ]

'''
    # id>>>name
    @staticmethod
    def jjc_output(num):
        out_msg_list = []
        out_msg='已为骑士君按点赞数由高到低\n查询到以下胜利队伍：\n'
        for i in range(len(num)):
            if num[i] in d.index:
                num[i] = d.loc[num[i]][0]                             #修改输出方式,0为image,1为文字
        for i in range(len(num)):
            if (i%10)==0 and i!=0:
                out_msg_list.append(num[i-10:i-5])
        for i in range(len(out_msg_list)):
            out_msg_list[i]=''.join(out_msg_list[i])
        for i in range(len(out_msg_list)):
            out_msg0 = ('第{}队:'.format(i+1) +'\n'+ out_msg_list[i] +'\n')
            out_msg += out_msg0
        return out_msg


    # name>id>name
    @staticmethod
    def query(msg):
        a=user_input(msg)         #返回list
        if a == 'Error':
            return '输入有误，请重新输入!'
        b=jjcsearch(a)        #num
        return (jjc_output(b))
'''
