import random

from hoshino import util
from ..chara import Chara


class Gacha(object):

    def __init__(self, pool_name:str="MIX"):
        super().__init__()
        self.load_pool(pool_name)


    def load_pool(self, pool_name:str):
        config = util.load_config(__file__)
        pool = config[pool_name]
        self.s3_prob = pool["s3_prob"]
        self.s2_prob = pool["s2_prob"]
        self.s1_prob = 1000 - self.s2_prob - self.s3_prob
        self.star3 = pool["star3"]
        self.star2 = pool["star2"]
        self.star1 = pool["star1"]
        
        self.s3_up_prob = self.star3["up_prob"] if 'up_prob' in self.star3 else 0
        self.s2_up_prob = self.star2["up_prob"] if 'up_prob' in self.star2 else 0
        self.s1_up_prob = self.star1["up_prob"] if 'up_prob' in self.star1 else 0
        
        s3Up = self.star3["up"] if 'up' in self.star3 else []
        s2Up = self.star2["up"] if 'up' in self.star2 else []
        s1Up = self.star1["up"] if 'up' in self.star1 else []
        self.up = s3Up + s2Up + s1Up


    def randUnit(self, unitList, total_prob):
        pick = random.randint(1, total_prob)
        # 如果有设置up,则先判断是否触发up
        if 'up' in unitList and 'up_prob' in unitList and len(unitList["up"]) > 0 and pick <= unitList["up_prob"]:
            return random.choice(unitList["up"]), True
            
        return random.choice(unitList["normal"]), False
            
            

    def gacha_one(self, s3_prob:int, s2_prob:int, s1_prob:int=None):
        '''
        sx_prob: x星概率，要求和为1000
        up_prob: UP角色概率（从3星划出）
        up_chara: UP角色名列表

        return: (单抽结果:Chara, 秘石数:int)
        ---------------------------
        |up|      |  20  |   78   |
        |   ***   |  **  |    *   |
        ---------------------------
        '''
        if s1_prob is None:
            s1_prob = 1000 - s3_prob - s2_prob
        total_ = s3_prob + s2_prob + s1_prob
        pick = random.randint(1, total_)
        if pick <= s3_prob:
            res, isUp = self.randUnit(self.star3, s3_prob)
            point = 100 if isUp else 50
            return Chara.fromname(res, 3), point
        elif pick <= s2_prob + s3_prob:
            res, isUp = self.randUnit(self.star2, s2_prob)
            return Chara.fromname(res, 2), 10
        else:
            res, isUp = self.randUnit(self.star1, s1_prob)
            return Chara.fromname(res, 1), 1


    def gacha_ten(self):
        result = []
        hiishi = 0
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2
        for _ in range(9):    # 前9连
            c, y = self.gacha_one(s3, s2, s1)
            result.append(c)
            hiishi += y
        c, y = self.gacha_one(s3, s2 + s1, 0)    # 保底第10抽
        result.append(c)
        hiishi += y

        return result, hiishi
        
    def gacha_bide_ten(self):
        result = []
        hiishi = 0
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2
        
        bide_index = random.randint(1, 10)
        
        for index in range(10):    # 前9连
            if index == bide_index:
                c, y = self.gacha_one(s3, 0, 0)
            else:
                c, y = self.gacha_one(s3, s2, s1)
            result.append(c)
            hiishi += y
        hiishi += y

        return result, hiishi

    def gacha_tenjou(self):
        result = {'up': [], 's3': [], 's2':[], 's1':[]}
        first_up_pos = 999999
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2
        for i in range(9 * 30):
            c, y = self.gacha_one(s3, s2, s1)
            if 100 == y:
                result['up'].append(c)
                first_up_pos = min(first_up_pos, 10 * ((i+1) // 9) + ((i+1) % 9))
            elif 50 == y:
                result['s3'].append(c)
            elif 10 == y:
                result['s2'].append(c)
            elif 1 == y:
                result['s1'].append(c)
            else:
                pass    # should never reach here
        for i in range(30):
            c, y = self.gacha_one(s3, s2 + s1, 0)
            if 100 == y:
                result['up'].append(c)
                first_up_pos = min(first_up_pos, 10 * (i+1))
            elif 50 == y:
                result['s3'].append(c)
            elif 10 == y:
                result['s2'].append(c)
            else:
                pass    # should never reach here
        result['first_up_pos'] = first_up_pos
        return result
