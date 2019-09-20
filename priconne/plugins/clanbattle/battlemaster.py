from datetime import datetime, timezone, timedelta
from .dao.sqlitedao import ClanDao, MemberDao, BattleDao

class BattleMaster(object):

    NOT_FOUND = 404

    NORM    = BattleDao.NORM
    LAST    = BattleDao.LAST
    EXT     = BattleDao.EXT
    TIMEOUT = BattleDao.TIMEOUT

    BOSS_HP = [6000000, 8000000, 10000000, 12000000, 15000000]
    SCORE_RATE = [
        1.0, 1.0, 1.2, 1.2, 1.5,
        1.4, 1.4, 1.8, 1.8, 2.0,
        2.0, 2.0, 2.5, 2.5, 3.0
    ]

    def __init__(self, group):
        super().__init__()
        self.group = group
        self.clandao = ClanDao()
        self.memberdao = MemberDao()

    
    @staticmethod
    def get_yyyymmdd(time):
        '''
        返回time对应的会战年月日。
        其中，年月为该期会战的年月；日为刷新周期对应的日期。
        会战为每月最后一星期，编程时认为mm月的会战一定在mm月20日至mm+1月10日之间，每日以5:00 UTC+8为界。
        注意：返回的年月日并不一定是自然时间，如2019年9月2日04:00:00我们认为对应2019年8月会战，日期仍为1号，将返回(2019,8,1)
        '''
        time = time.astimezone(timezone(timedelta(hours=3)))  # UTC+3 的0点恰好可以作为分界线
        yyyy = time.year
        mm = time.month
        dd = time.day
        if dd < 10:
            mm = mm - 1
        if mm < 1:
            mm = 12
            yyyy = yyyy - 1
        return (yyyy, mm, dd)


    def get_battledao(self, cid, time):
        yyyy, mm, _ = self.get_yyyymmdd(time)
        return BattleDao(self.group, cid, yyyy, mm)


    def has_clan(self, cid):
        return True if self.clandao.find_one(self.group, cid) else False


    def get_clan(self, cid):
        return self.clandao.find_one(self.group, cid)


    def add_clan(self, cid, name):
        return self.clandao.add({'gid': self.group, 'cid': cid, 'name': name})


    def list_clan(self):
        return self.clandao.find_by_gid(self.group)


    def mod_clan(self, cid, name):
        return self.clandao.modify({'gid': self.group, 'cid': cid, 'name': name})


    def del_clan(self, cid):
        return self.clandao.delete(self.group, cid)


    def add_member(self, uid, alt, name, cid):
        return self.memberdao.add({'uid': uid, 'alt': alt, 'name': name, 'gid': self.group, 'cid': cid})


    def get_member(self, uid, alt):
        mem = self.memberdao.find_one(uid, alt)
        return mem if mem and mem['gid'] == self.group else None


    def list_member(self):
        return self.memberdao.find_by_gid(self.group)


    def list_account(self, uid):
        return self.memberdao.find_by_gid_uid(self.group, uid)

    
    def mod_member(self, uid, alt, new_name, new_cid):
        return self.memberdao.modify({'uid': uid, 'alt': alt, 'name': new_name, 'gid': self.group, 'cid': new_cid})


    def del_member(self, uid, alt):
        return self.memberdao.delete(uid, alt)


    def add_challenge(self, uid, alt, round_, boss, dmg, flag, time):
        mem = self.get_member(uid, alt)
        if not mem or mem['gid'] != self.group:
            return BattleMaster.NOT_FOUND
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
            return BattleMaster.NOT_FOUND
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


    # def del_challenge(self, eid, uid, alt, time):
    #     mem = self.get_member(uid, alt)
    #     if not mem or mem['gid'] != self.group:
    #         return BattleMaster.NOT_FOUND
    #     # TODO


    def get_challenge(self, eid, cid, time):
        dao = self.get_battledao(cid, time)
        return dao.find_one(eid)


    def list_challenge_of_user(self, uid, alt, time):
        mem = self.memberdao.find_one(uid, alt)
        if not mem or mem['gid'] != self.group:
            return []
        dao = self.get_battledao(mem['cid'], time)
        return dao.find_by_uid_alt(uid, alt)


    def list_challenge_of_day(self, cid, time):
        ret = []
        _, _, day = self.get_yyyymmdd(time)
        dao = self.get_battledao(cid, time)
        for c in dao.find_all():
            if day == self.get_yyyymmdd(c['time']):
                ret.append(c)
        return ret


    def list_challenge_of_user_of_day(self, uid, alt, time):
        ret = []
        _, _, day = self.get_yyyymmdd(time)
        mem = self.memberdao.find_one(uid, alt)
        if not mem or mem['gid'] != self.group:
            return []
        dao = self.get_battledao(mem['cid'], time)
        for c in dao.find_by_uid_alt(uid, alt):
            if day == self.get_yyyymmdd(c['time']):
                ret.append(c)
        return ret


    def get_challenge_progress(self, cid, time):
        '''
        return (round_, boss, remain_hp)
        '''
        dao = self.get_battledao(cid, time)
        challens = dao.find_all()
        if not len(challens):
            return ( 1, 1, self.get_boss_hp(1) )
        round_ = challens[-1]['round']
        boss = challens[-1]['boss']
        remain_hp = self.get_boss_hp(boss)
        for challen in reversed(challens):
            if challen['round'] == round_ and challen['boss'] == boss:
                remain_hp = remain_hp - challen['dmg']
            else:
                break
        if remain_hp <= 0:
            round_, boss = self.next_boss(round_, boss)
            remain_hp = self.get_boss_hp(boss)
        return (round_, boss, remain_hp)


    @staticmethod
    def next_boss(round_, boss):
        boss = boss + 1
        if boss > 5:
            boss = 1
            round_ = round_ + 1
        return (round_, boss)


    @staticmethod
    def get_stage(round_):
        return 3 if round_ >= 11 else 2 if round_ >= 4 else 1


    @staticmethod
    def get_boss_hp(boss):
        return BattleMaster.BOSS_HP[ boss-1 ]


    @staticmethod
    def get_score_rate(round_, boss):
        stage = BattleMaster.get_stage(round_)
        return BattleMaster.SCORE_RATE[ 5*(stage-1) + boss-1 ]

    @staticmethod
    def int2kanji(x):
        kanji = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        return kanji[x]

