import time
import requests
import ujson as json

from hoshino import util
from . import sv
from ..chara import Chara

logger = sv.logger

class Arena(object):

    @staticmethod
    def __get_auth_key():
        config = util.load_config(__file__)
        return config["AUTH_KEY"]


    @staticmethod
    def do_query(id_list):
        
        id_list = [ x * 100 + 1 for x in id_list ]
        logger.debug(f'id_list={id_list}')
        
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'authorization': Arena.__get_auth_key()
        }
        payload = {"_sign": "a", "def": id_list, "nonce": "a", "page": 1, "sort": 1, "ts": int(time.time()), "region": 1}
        
        logger.info(f'Arena query payload={json.dumps(payload)}')
        
        resp = requests.post('https://api.pcrdfans.com/x/v1/search', headers=header, data=json.dumps(payload))
        res = resp.json()
        logger.debug(f'len(res)={len(res)}')

        if res['code']:
            logger.error(f"Arena query failed. \nResponse={res}")
            return None

        res = res['data']['result']
        res = [
            {
                'atk': [ Chara(c['id'] // 100, c['star'], c['equip']) for c in entry['atk'] ],
                'up': entry['up'],
                'down': entry['down'],
            } for entry in res
        ]
        return res

