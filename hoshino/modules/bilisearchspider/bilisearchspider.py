from hoshino import Service, priv, aiorequests
from hoshino.typing import MessageSegment, CQEvent
from hoshino.modules.priconne.news.spider import BaseSpider

from dataclasses import dataclass
from typing import List, Union
import hoshino, json, os

sv_help = '''
- [添加B站爬虫 关键词 ] 添加爬取关键词。每次添加一个，可添加多次
- [查看B站爬虫]  查看当前爬取关键词列表
- [删除B站爬虫 关键词 ] 删除指定爬取关键词
'''.strip()

sv = Service(
    name='B站爬虫',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=False,  # 是否默认启用
    bundle='订阅',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-B站爬虫"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@dataclass
class Item:
    idx: Union[str, int]
    pic: str = ""
    content: str = ""

    def __eq__(self, other):
        return self.idx == other.idx


class BiliSearchSpider(BaseSpider):
    url = {}
    src_name = "B站爬虫"
    idx_cache = {}
    item_cache = {}

    @classmethod
    def set_url(cls, gid, keyword_list):
        cls.url[gid] = [
            f'http://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}&order=pubdate&duration=0&tids_1=0'
            for keyword in keyword_list]
        if gid not in cls.idx_cache.keys(): cls.idx_cache[gid] = []
        if gid not in cls.item_cache.keys(): cls.item_cache[gid] = []

    @staticmethod
    async def get_response(url) -> aiorequests.AsyncResponse:
        resp = await aiorequests.get(url)
        resp.raise_for_status()
        return resp

    @classmethod
    async def get_update(cls, gid) -> List[Item]:
        updates_all = []
        items_all = []
        for url in cls.url[gid]:
            resp = await cls.get_response(url)
            items = await cls.get_items(resp)
            updates_all.extend([i for i in items if i.idx not in cls.idx_cache[gid] and i not in updates_all])
            items_all.extend(items)
        if updates_all:
            cls.idx_cache[gid] = set(i.idx for i in items_all)
            cls.item_cache[gid] = items_all
        return updates_all

    @staticmethod
    async def get_items(resp: aiorequests.AsyncResponse):
        content = await resp.json()
        return [
            Item(idx=result['arcurl'],
                 pic=result['pic'],
                 content="{}\nup主: {}\n{}".format(
                     result['title'].replace('<em class=\"keyword\">', '').replace('</em>', ''), result['author'],
                     result['arcurl'])
                 ) for result in content['data']['result']
        ]

    @classmethod
    def format_items(cls, items):
        ret = [f'{cls.src_name}发现了新发布的视频:']
        ret.extend([i.content for i in items])
        return ret


def load_config():
    try:
        config_path = './hoshino/modules/bilisearchspider/spider_conifg.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf8') as config_file:
                return json.load(config_file)
        else:
            return {}
    except:
        return {}


def save_config(config):
    try:
        with open('./hoshino/modules/bilisearchspider/spider_conifg.json', 'w', encoding='utf8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        return True
    except:
        return False


async def spider_work(spider: BaseSpider, bot, gid, sv: Service, TAG):
    if not spider.item_cache[gid]:
        await spider.get_update(gid)
        sv.logger.info(f'群{gid}的{TAG}缓存为空，已加载至最新')
        return
    updates = await spider.get_update(gid)
    if not updates:
        sv.logger.info(f'群{gid}的{TAG}未检索到新视频')
        return
    sv.logger.info(f'群{gid}的{TAG}检索到{len(updates)}个新视频！')
    msg_list = spider.format_items(updates)
    for i in range(len(updates)):
        pic = MessageSegment.image('http:' + updates[i].pic)
        msg = f'{msg_list[0]}{pic}{msg_list[i + 1]}'
        await bot.send_group_msg(group_id=int(gid), message=msg)


@sv.on_prefix('添加B站爬虫')
async def add_spider_keyword(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    s = ev.message.extract_plain_text()
    config = load_config()
    gid = str(ev.group_id)
    if gid in config.keys():
        if s not in config[gid]:
            config[gid].append(s)
        else:
            await bot.finish(ev, '此群已经添加过该关键词，请勿重复添加')
    else:
        config[gid] = [s]
    if save_config(config):
        await bot.send(ev, f'添加关键词"{s}"成功!')
        # 重置群gid的item_cache和idx_cache，并重新加载缓存
        BiliSearchSpider.item_cache[gid] = []
        BiliSearchSpider.idx_cache[gid] = []
        await bili_search_spider()
    else:
        await bot.send(ev, '添加关键词失败，请重试')


@sv.on_fullmatch('查看B站爬虫')
async def get_spider_keyword_list(bot, ev: CQEvent):
    config = load_config()
    gid = str(ev.group_id)
    if gid in config.keys() and config[gid]:
        msg = 'B站爬虫已开启!\n此群设置的爬虫关键词为:\n' + '\n'.join(config[gid])
    else:
        msg = '此群还未添加B站爬虫关键词'
    await bot.send(ev, msg)


@sv.on_prefix('删除B站爬虫')
async def delete_spider_keyword(bot, ev: CQEvent):
    config = load_config()
    s = ev.message.extract_plain_text()
    gid = str(ev.group_id)
    if gid in config.keys() and s in config[gid]:
        config[gid].remove(s)
        msg = f'删除关键词"{s}"成功'
    else:
        msg = f'删除失败, 此群未设置关键词"{s}"'
    if not save_config(config):
        await bot.finish(ev, '删除爬虫关键词失败，请重试')
    await bot.send(ev, msg)


@sv.scheduled_job('cron', minute='*/5', second='30', jitter=20)
async def bili_search_spider():
    bot = hoshino.get_bot()
    config = load_config()
    for gid in config.keys():
        BiliSearchSpider.set_url(gid, config[gid])
        await spider_work(BiliSearchSpider, bot, gid, sv, 'B站搜索爬虫')
