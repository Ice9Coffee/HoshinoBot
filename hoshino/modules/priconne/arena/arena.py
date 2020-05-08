import os
import time
import base64
from collections import defaultdict
try:
    import ujson as json
except:
    import json

from hoshino import aiorequests, util
from . import sv
from ..chara import Chara

logger = sv.logger

'''
Database for arena likes & dislikes
DB is a dict like: { 'md5_id': {'like': set(qq), 'dislike': set(qq)} }
'''
DB_PATH = os.path.expanduser('~/.hoshino/arena_db.json')
DB = {}
try:
    with open(DB_PATH, encoding='utf8') as f:
        DB = json.load(f)
    for k in DB:
        DB[k] = {
            'like': set(DB[k].get('like', set())),
            'dislike': set(DB[k].get('dislike', set()))
        }
except FileNotFoundError:
    logger.warning(f'arena_db.json not found, will create when needed.')

def dump_db():
    '''
    Dump the arena databese.
    json do not accept set object, this function will help to convert.
    '''
    j = {}
    for k in DB:
        j[k] = {
            'like': list(DB[k].get('like', set())),
            'dislike': list(DB[k].get('dislike', set()))
        }
    with open(DB_PATH, 'w', encoding='utf8') as f:
        json.dump(j, f, ensure_ascii=False)

def get_like_num(id_):
    return len(DB.get(id_, {}).get('like', set()))

def add_like(id_, uid):
    e = DB.get(id_, {})
    l = e.get('like', set())
    k = e.get('dislike', set())
    l.add(uid)
    k.discard(uid)
    e['like'] = l
    e['dislike'] = k
    DB[id_] = e

def get_dislike_num(id_):
    return len(DB.get(id_, {}).get('dislike', set()))

def add_dislike(id_, uid):
    e = DB.get(id_, {})
    l = e.get('like', set())
    k = e.get('dislike', set())
    l.discard(uid)
    k.add(uid)
    e['like'] = l
    e['dislike'] = k
    DB[id_] = e


_last_query_time = 0
quick_key_dic = {}      # {quick_key: true_id}

def refresh_quick_key_dic():
    global _last_query_time
    now = time.time()
    if now - _last_query_time > 300:
        quick_key_dic.clear()
    _last_query_time = now


def gen_quick_key(true_id:str, user_id:int) -> str:
    qkey = int(true_id[-6:], 16)
    while qkey in quick_key_dic and quick_key_dic[qkey] != true_id:
        qkey = (qkey + 1) & 0xffffff
    quick_key_dic[qkey] = true_id
    mask = user_id & 0xffffff
    qkey ^= mask
    return base64.b32encode(qkey.to_bytes(3, 'little')).decode()[:5]


def get_true_id(quick_key:str, user_id:int) -> str:
    mask = user_id & 0xffffff
    if not isinstance(quick_key, str) or len(quick_key) != 5:
        return None
    qkey = (quick_key + '===').encode()
    qkey = int.from_bytes(base64.b32decode(qkey, casefold=True, map01=b'I'), 'little')
    qkey ^= mask
    return quick_key_dic.get(qkey, None)


def __get_auth_key():
    config = util.load_config(__file__)
    return config["AUTH_KEY"]


async def do_query(id_list, user_id, region=1):
    id_list = [ x * 100 + 1 for x in id_list ]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'authorization': __get_auth_key()
    }
    payload = {"_sign": "a", "def": id_list, "nonce": "a", "page": 1, "sort": 1, "ts": int(time.time()), "region": region}
    logger.debug(f'Arena query {payload=}')
    try:
        resp = await aiorequests.post('https://api.pcrdfans.com/x/v1/search', headers=header, json=payload)
        res = await resp.json()
        logger.debug(f'len(res)={len(res)}')
    except Exception as e:
        logger.exception(e)
        return None

    if res['code']:
        logger.error(f"Arena query failed.\nResponse={res}\nPayload={payload}")
        return None

    res = res['data']['result']
    res = [
        {
            'qkey': gen_quick_key(entry['id'], user_id),
            'atk': [ Chara(c['id'] // 100, c['star'], c['equip']) for c in entry['atk'] ],
            'up': entry['up'],
            'down': entry['down'],
            'my_up': get_like_num(entry['id']),
            'my_down': get_dislike_num(entry['id'])
        } for entry in res
    ]
    return res


async def do_like(qkey, user_id, action):
    true_id = get_true_id(qkey, user_id)
    if true_id is None:
        raise KeyError
    add_like(true_id, user_id) if action > 0 else add_dislike(true_id, user_id)
    dump_db()
    # TODO: upload to website
