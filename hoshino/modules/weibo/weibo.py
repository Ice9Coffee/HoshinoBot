# -*- coding: UTF-8 -*-

import json
import random
import sys
import asyncio
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep

import httpx
from lxml import etree
from hoshino import logger
from .exception import *

class WeiboSpider(object):
    def __init__(self, config):
        """Weibo类初始化"""
        self.validate_config(config)
        self.filter = config['filter'] 
        self.user_id = config['user_id']
        self.received_weibo_ids = []
        self.__recent = False
        asyncio.get_event_loop().run_until_complete(self._async_init())
    
    async def _async_init(self):
        self.user = await self.get_user_info(self.user_id)
    
    async def get_json(self, params):
        """获取网页中json数据"""
        url = 'https://m.weibo.cn/api/container/getIndex?'
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=10.0) # sometimes timeout
            return r.json()

    async def get_user_info(self, user_id):
        """获取用户信息"""
        params = {'containerid': '100505' + str(user_id)}
        js = await self.get_json(params)
        if js['ok']:
            info = js['data']['userInfo']
            user_info = OrderedDict()
            user_info['id'] = user_id
            user_info['screen_name'] = info.get('screen_name', '')
            user_info['gender'] = info.get('gender', '')
            params = {
                'containerid':
                '230283' + str(user_id) + '_-_INFO'
            }
            zh_list = [
                u'生日', u'所在地', u'小学', u'初中', u'高中', u'大学', u'公司', u'注册时间',
                u'阳光信用'
            ]
            en_list = [
                'birthday', 'location', 'education', 'education', 'education',
                'education', 'company', 'registration_time', 'sunshine'
            ]
            for i in en_list:
                user_info[i] = ''
            js =  await self.get_json(params)
            if js['ok']:
                cards = js['data']['cards']
                if isinstance(cards, list) and len(cards) > 1:
                    card_list = cards[0]['card_group'] + cards[1]['card_group']
                    for card in card_list:
                        if card.get('item_name') in zh_list:
                            user_info[en_list[zh_list.index(
                                card.get('item_name'))]] = card.get(
                                    'item_content', '')
            user_info['statuses_count'] = info.get('statuses_count', 0)
            user_info['followers_count'] = info.get('followers_count', 0)
            user_info['follow_count'] = info.get('follow_count', 0)
            user_info['description'] = info.get('description', '')
            user_info['profile_url'] = info.get('profile_url', '')
            user_info['profile_image_url'] = info.get('profile_image_url', '')
            user_info['avatar_hd'] = info.get('avatar_hd', '')
            user_info['urank'] = info.get('urank', 0)
            user_info['mbrank'] = info.get('mbrank', 0)
            user_info['verified'] = info.get('verified', False)
            user_info['verified_type'] = info.get('verified_type', 0)
            user_info['verified_reason'] = info.get('verified_reason', '')
            user = self.standardize_info(user_info)
            return user

    def clear_buffer(self):
        self.received_weibo_ids.clear()

    def validate_config(self, config):
        """验证配置是否正确"""
        exist_argument_list = ['user_id']
        true_false_argument_list = ['filter']

        for argument in true_false_argument_list:
            if argument not in config:
                raise NotFoundError(f'未找到参数{argument}')
            if config[argument] != True and config[argument] != False:
                raise ParseError(f'{argument} 值应为 True 或 False')

        for argument in exist_argument_list: 
            if argument not in config:
                raise NotFoundError(f'未找到参数{argument}')

    def get_pics(self, weibo_info):
        """获取微博原始图片url"""
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            pic_list = [pic['large']['url'] for pic in pic_info]
        else:
            pic_list = []
        return pic_list

    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get('pic_video')
        if live_photo:
            prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
            for i in live_photo.split(','):
                if len(i.split(':')) == 2:
                    url = prefix + i.split(':')[1] + '.mov'
                    live_photo_list.append(url)
            return live_photo_list

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if weibo_info['page_info'].get('media_info') and weibo_info[
                    'page_info'].get('type') == 'video':
                media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                    if not video_url:
                        video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                            if not video_url:
                                video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return video_url_list

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_article_url(self, selector):
        """获取微博中头条文章的url"""
        article_url = ''
        text = selector.xpath('string(.)')
        if text.startswith(u'发布了头条文章'):
            url = selector.xpath('//a/@data-url')
            if url and url[0].startswith('http://t.cn'):
                article_url = url[0]
        return article_url

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ','.join(topic_list)
        return topics

    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)

    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u"刚刚" in created_at:
            created_at = datetime.now().strftime("%Y-%m-%d")
            self.__recent = True
        elif u"分钟" in created_at:
            minute = created_at[:created_at.find(u"分钟")]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
            self.__recent = True
        elif u"小时" in created_at:
            hour = created_at[:created_at.find(u"小时")]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
            self.__recent = False
        elif u"昨天" in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime("%Y-%m-%d")
            self.__recent = False
        elif created_at.count('-') == 1:
            year = datetime.now().strftime("%Y")
            created_at = year + "-" + created_at
            self.__recent = False
        return created_at

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                        type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u"\u200b", "").encode(
                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        return weibo

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['id'] = int(weibo_info['id'])
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = etree.HTML(text_body).xpath('string(.)')
        weibo['article_url'] = self.get_article_url(selector)
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector)
        weibo['at_users'] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    def print_one_weibo(self, weibo):
        """打印一条微博"""
        try:
            logger.info(u'微博id：%d' % weibo['id'])
            logger.info(u'微博正文：%s' % weibo['text'])
            logger.info(u'原始图片url：%s' % weibo['pics'])
            logger.info(u'微博位置：%s' % weibo['location'])
            logger.info(u'发布时间：%s' % weibo['created_at'])
            logger.info(u'发布工具：%s' % weibo['source'])
            logger.info(u'点赞数：%d' % weibo['attitudes_count'])
            logger.info(u'评论数：%d' % weibo['comments_count'])
            logger.info(u'转发数：%d' % weibo['reposts_count'])
            logger.info(u'话题：%s' % weibo['topics'])
            logger.info(u'@用户：%s' % weibo['at_users'])
            logger.info(u'url：https://m.weibo.cn/detail/%d' % weibo['id'])
        except OSError:
            pass
    
    def print_weibo(self, weibo):
        """打印微博，若为转发微博，会同时打印原创和转发部分"""
        if weibo.get('retweet'):
            logger.info('*' * 100)
            logger.info(u'转发部分：')
            self.print_one_weibo(weibo['retweet'])
            logger.info('*' * 100)
            logger.info(u'原创部分：')
        self.print_one_weibo(weibo)
        logger.info('-' * 120)

    def get_username(self):
        return self.user["screen_name"]
    
    def get_user_id(self):
        return self.user_id

    async def get_weibo_json(self, page):
        """获取网页中微博json数据"""
        params = {
            'containerid': '107603' + self.get_user_id(),
            'page': page
        }
        js = await self.get_json(params)
        return js

    async def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(5):
            url = 'https://m.weibo.cn/detail/%s' % id
            async with httpx.AsyncClient() as client:
                html = await client.get(url)
                html = html.text
                html = html[html.find('"status":'):]
                html = html[:html.rfind('"hotScheme"')]
                html = html[:html.rfind(',')]
                html = '{' + html + '}'
                js = json.loads(html, strict=False)
                weibo_info = js.get('status')
                if weibo_info:
                    weibo = self.parse_weibo(weibo_info)
                    return weibo
                asyncio.sleep(random.randint(6, 10))

    def print_user_info(self):
        """打印用户信息"""
        logger.info('+' * 100)
        logger.info(u'用户信息')
        logger.info(u'用户id：%s' % self.user['id'])
        logger.info(u'用户昵称：%s' % self.user['screen_name'])
        gender = u'女' if self.user['gender'] == 'f' else u'男'
        logger.info(u'性别：%s' % gender)
        logger.info(u'生日：%s' % self.user['birthday'])
        logger.info(u'所在地：%s' % self.user['location'])
        logger.info(u'教育经历：%s' % self.user['education'])
        logger.info(u'公司：%s' % self.user['company'])
        logger.info(u'阳光信用：%s' % self.user['sunshine'])
        logger.info(u'注册时间：%s' % self.user['registration_time'])
        logger.info(u'微博数：%d' % self.user['statuses_count'])
        logger.info(u'粉丝数：%d' % self.user['followers_count'])
        logger.info(u'关注数：%d' % self.user['follow_count'])
        logger.info(u'url：https://m.weibo.cn/profile/%s' % self.user['id'])
        if self.user.get('verified_reason'):
            logger.info(self.user['verified_reason'])
        logger.info(self.user['description'])
        logger.info('+' * 100)

    async def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = weibo_info.get('isLongText')
            if retweeted_status and retweeted_status.get('id'):  # 转发
                retweet_id = retweeted_status.get('id')
                is_long_retweet = retweeted_status.get('isLongText')
                if is_long:
                    weibo = await self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = await self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                retweet['created_at'] = self.standardize_date(
                    retweeted_status['created_at'])
                weibo['retweet'] = retweet
            else:  # 原创
                if is_long:
                    weibo = await self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(
                weibo_info['created_at'])
            return weibo
        except Exception as e:
            logger.exception(e)
            self.__recent = False

    async def get_latest_weibos(self):
        try:
            latest_weibos = []
            js = await self.get_weibo_json(1)
            if js['ok']:
                weibos = js['data']['cards']
                for w in weibos:
                    if w['card_type'] == 9:
                        wb = await self.get_one_weibo(w)
                        if wb:
                            if not self.__recent:
                                continue
                            if wb["id"] in self.received_weibo_ids:
                                continue
                            if (not self.filter) or (
                                    'retweet' not in wb.keys()):
                                latest_weibos.append(wb)
                                self.received_weibo_ids.append(wb["id"])
                                self.print_weibo(wb)
                            
            return latest_weibos
        except Exception as e:
            logger.exception(e)
            return []