from datetime import datetime, timezone, timedelta

from hoshino import util
from .dao.sqlitedao import ClanDao, MemberDao, BattleDao
from .exception import NotFoundError

def get_config():
    return util.load_config(__file__)


class BattleMaster(object):

    NORM    = BattleDao.NORM
    LAST    = BattleDao.LAST
    EXT     = BattleDao.EXT
    TIMEOUT = BattleDao.TIMEOUT

    SERVER_JP = ClanDao.SERVER_JP
    SERVER_TW = ClanDao.SERVER_TW
    SERVER_CN = ClanDao.SERVER_CN

    SERVER_JP_NAME = ('jp', 'JP', 'Jp', '日', '日服', str(SERVER_JP))
    SERVER_TW_NAME = ('tw', 'TW', 'Tw', '台', '台服', str(SERVER_TW))
    SERVER_CN_NAME = ('cn', 'CN', 'Cn', '国', '国服', 'B', 'B服', str(SERVER_CN))
    
    def __init__(self, group):
        super().__init__()
        self.group = group
        self.clandao = ClanDao()
        self.memberdao = MemberDao()
        self.config = get_config()


    @staticmethod
    def get_timezone_num(server):
        return 9 if BattleMaster.SERVER_JP == server else 8

    
    @staticmethod
    def get_yyyymmdd(time, zone_num:int=8):
        '''
        返回time对应的会战年月日。
        其中，年月为该期会战的年月；日为刷新周期对应的日期。
        会战为每月最后一星期，编程时认为mm月的会战一定在mm月20日至mm+1月10日之间，每日以5:00 UTC+8为界。
        注意：返回的年月日并不一定是自然时间，如2019年9月2日04:00:00我们认为对应2019年8月会战，日期仍为1号，将返回(2019,8,1)
        '''
        # 日台服均为当地时间凌晨5点更新，故减5
        time = time.astimezone(timezone(timedelta(hours=zone_num-5)))
        yyyy = time.year
        mm = time.month
        dd = time.day
        if dd < 3:
            mm = mm - 1
        if mm < 1:
            mm = 12
            yyyy = yyyy - 1
        return (yyyy, mm, dd)


    @staticmethod
    def next_boss(round_:int, boss:int):
        return (round_, boss + 1) if boss < 5 else (round_ + 1, 1)


    @staticmethod
    def get_stage(round_, server):
        if server == BattleMaster.SERVER_JP:
            return 5 if round_ >= 41 else 4 if round_ >= 31 else 3 if round_ >= 11 else 2 if round_ >= 4 else 1
        else:
            return 5 if round_ >= 45 else 4 if round_ >= 35 else 3 if round_ >= 11 else 2 if round_ >= 4 else 1


    def get_boss_info(self, round_, boss, server):
        """@return: boss_max_hp, score_rate"""
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        boss_hp = config[ config["BOSS_HP"][server] ][ stage-1 ][ boss-1 ]
        score_rate = config[ config["SCORE_RATE"][server] ][ stage-1 ][ boss-1 ]
        return boss_hp, score_rate


    def get_boss_hp(self, round_, boss, server):
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        return config[ config["BOSS_HP"][server] ][ stage-1 ][ boss-1 ]


    def get_score_rate(self, round_, boss, server):
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        return config[ config["SCORE_RATE"][server] ][ stage-1 ][ boss-1 ]


    @staticmethod
    def int2kanji(x):
        if 0 <= x <= 50:
            return '零一二三四五六七八九十⑪⑫⑬⑭⑮⑯⑰⑱⑲廿㉑㉒㉓㉔㉕㉖㉗㉘㉙卅㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'[x]
        raise ValueError("'x' should in range [0, 50]")

    @staticmethod
    def get_server_code(server_name):
        if server_name in BattleMaster.SERVER_JP_NAME:
            return BattleMaster.SERVER_JP
        elif server_name in BattleMaster.SERVER_TW_NAME:
            return BattleMaster.SERVER_TW
        elif server_name in BattleMaster.SERVER_CN_NAME:
            return BattleMaster.SERVER_CN
        else:
            return -1


    def get_battledao(self, cid, time):
        clan = self.get_clan(cid)
        zone_num = self.get_timezone_num(clan['server'])
        yyyy, mm, _ = self.get_yyyymmdd(time, zone_num)
        return BattleDao(self.group, cid, yyyy, mm)


    def add_clan(self, cid, name, server):
        return self.clandao.add({'gid': self.group, 'cid': cid, 'name': name, 'server': server})
    def del_clan(self, cid):
        return self.clandao.delete(self.group, cid)
    def mod_clan(self, cid, name, server):
        return self.clandao.modify({'gid': self.group, 'cid': cid, 'name': name, 'server': server})
    def has_clan(self, cid):
        return True if self.clandao.find_one(self.group, cid) else False
    def get_clan(self, cid):
        return self.clandao.find_one(self.group, cid)
    def list_clan(self):
        return self.clandao.find_by_gid(self.group)


    def add_member(self, uid, alt, name, cid):
        return self.memberdao.add({'uid': uid, 'alt': alt, 'name': name, 'gid': self.group, 'cid': cid})
    def del_member(self, uid, alt):
        return self.memberdao.delete(uid, alt)
    def clear_member(self, cid=None):
        return self.memberdao.delete_by(gid=self.group, cid=cid)
    def mod_member(self, uid, alt, new_name, new_cid):
        return self.memberdao.modify({'uid': uid, 'alt': alt, 'name': new_name, 'gid': self.group, 'cid': new_cid})
    def has_member(self, uid, alt):
        mem = self.memberdao.find_one(uid, alt)
        return True if mem and mem['gid'] == self.group else False
    def get_member(self, uid, alt):
        mem = self.memberdao.find_one(uid, alt)
        return mem if mem and mem['gid'] == self.group else None
    def list_member(self, cid=None):
        return self.memberdao.find_by(gid=self.group, cid=cid)
    def list_account(self, uid):
        return self.memberdao.find_by(gid=self.group, uid=uid)


    def add_challenge(self, uid, alt, round_, boss, dmg, flag, time):
        mem = self.get_member(uid, alt)
        if not mem or mem['gid'] != self.group:
            raise NotFoundError('未找到成员')
        challenge = {
            'uid':   uid,
            'alt':   alt,
            'time':  time,
            'round': round_,
            'boss':  boss,
            'dmg':   dmg,
            'flag':  flag
        }
        dao = self.get_battledao(mem['cid'], time)
        return dao.add(challenge)

    def mod_challenge(self, eid, uid, alt, round_, boss, dmg, flag, time):
        mem = self.get_member(uid, alt)
        if not mem or mem['gid'] != self.group:
            raise NotFoundError('未找到成员')
        challenge = {
            'eid':   eid,
            'uid':   uid,
            'alt':   alt,
            'time':  time,
            'round': round_,
            'boss':  boss,
            'dmg':   dmg,
            'flag':  flag
        }
        dao = self.get_battledao(mem['cid'], time)
        return dao.modify(challenge)

    def del_challenge(self, eid, cid, time):
        dao = self.get_battledao(cid, time)
        return dao.delete(eid)

    def get_challenge(self, eid, cid, time):
        dao = self.get_battledao(cid, time)
        return dao.find_one(eid)

    def list_challenge(self, cid, time):
        dao = self.get_battledao(cid, time)
        return dao.find_all()

    def list_challenge_of_user(self, uid, alt, time):
        mem = self.memberdao.find_one(uid, alt)
        if not mem or mem['gid'] != self.group:
            return []
        dao = self.get_battledao(mem['cid'], time)
        return dao.find_by(uid=uid, alt=alt)


    @staticmethod
    def filt_challenge_of_day(challenge_list, time, zone_num:int=8):
        _, _, day = BattleMaster.get_yyyymmdd(time, zone_num)
        return list(filter(lambda challen: day == BattleMaster.get_yyyymmdd(challen['time'], zone_num)[2], challenge_list))


    def list_challenge_of_day(self, cid, time, zone_num:int=8):
        return self.filt_challenge_of_day(self.list_challenge(cid, time), time, zone_num)


    def list_challenge_of_user_of_day(self, uid, alt, time, zone_num:int=8):
        return self.filt_challenge_of_day(self.list_challenge_of_user(uid, alt, time), time, zone_num)


    def stat_challenge(self, cid, time, only_one_day=True, zone_num:int=8):
        '''
        统计每个成员的出刀
        return [(member, [challenge])]
        '''
        ret = []
        mem = self.list_member(cid)
        dao = self.get_battledao(cid, time)
        for m in mem:
            challens = dao.find_by(uid=m['uid'], alt=m['alt'])
            if only_one_day:
                challens = self.filt_challenge_of_day(challens, time, zone_num)
            ret.append((m, challens))
        return ret

    
    def stat_damage(self, cid, time):
        '''
        统计cid会各成员的本月各Boss伤害总量
        :return: [(uid, alt, name, [total_dmg, dmg1, ..., dmg5])]
        '''
        clan = self.get_clan(cid)
        if not clan:
            raise NotFoundError(f'未找到公会{cid}')
        server = clan['server']
        stat = self.stat_challenge(cid, time, only_one_day=False, zone_num=self.get_timezone_num(server))
        ret = []
        for mem, challens in stat:
            dmgs = [0] * 6
            for ch in challens:
                d = ch['dmg']
                dmgs[0] += d
                dmgs[ch['boss']] += d
            ret.append((mem['uid'], mem['alt'], mem['name'], dmgs))
        return ret


    def stat_score(self, cid, time):
        '''
        统计cid会各成员的本月总分数
        :return: [(uid,alt,name,score)]
        '''
        clan = self.get_clan(cid)
        if not clan:
            raise NotFoundError(f'未找到公会{cid}')
        server = clan['server']
        stat = self.stat_challenge(cid, time, only_one_day=False, zone_num=self.get_timezone_num(server))
        ret = [
            (mem['uid'], mem['alt'], mem['name'], sum(map(lambda ch: round(self.get_score_rate(ch['round'], ch['boss'], server) * ch['dmg']), challens)))
            for mem, challens in stat
        ]
        return ret


    def list_challenge_remain(self, cid, time):
        '''
        return [(uid,alt,name,remain_n,remain_e)]

        norm + timeout + last == 3 - remain_n       // 正常出刀数 == 3 - 余刀数
        last - ext == remain_e                      // 尾刀数 - 补时刀数 == 补时余刀
        challen_cnt == norm + last + ext + timeout  // 列表长度 == 所有出刀
        故有==>
        remain_n = 3 - (norm + timeout + last)
        remain_e = last - ext
        '''
        def count(challens):
            norm = 0
            last = 0
            ext = 0
            timeout = 0
            for ch in challens:
                f = ch['flag']
                if f & BattleMaster.EXT:
                    ext = ext + 1
                elif f & BattleMaster.LAST:
                    last = last + 1
                elif f & BattleMaster.TIMEOUT:
                    timeout = timeout + 1
                else:
                    norm = norm + 1
            return norm, last, ext, timeout

        clan = self.get_clan(cid)
        if not clan:
            raise NotFoundError(f'未找到公会{cid}')
        ret = []
        stat = self.stat_challenge(cid, time, only_one_day=True, zone_num=self.get_timezone_num(clan['server']))
        for mem, challens in stat:
            norm, last, ext, timeout = count(challens)
            r = (
                mem['uid'], mem['alt'], mem['name'],
                3 - (norm + timeout + last),
                last - ext,
            )
            ret.append(r)
        return ret


    def get_challenge_progress(self, cid, time):
        '''
        return (round, boss, remain_hp)
        '''
        clan = self.get_clan(cid)
        if not clan:
            return None
        server = clan['server']
        dao = self.get_battledao(cid, time)
        challens = dao.find_all()
        if not len(challens):
            return ( 1, 1, self.get_boss_hp(1, 1, server) )
        round_ = challens[-1]['round']
        boss = challens[-1]['boss']
        remain_hp = self.get_boss_hp(round_, boss, server)
        for challen in reversed(challens):
            if challen['round'] == round_ and challen['boss'] == boss:
                remain_hp = remain_hp - challen['dmg']
            else:
                break
        if remain_hp <= 0:
            round_, boss = self.next_boss(round_, boss)
            remain_hp = self.get_boss_hp(round_, boss, server)
        return (round_, boss, remain_hp)
