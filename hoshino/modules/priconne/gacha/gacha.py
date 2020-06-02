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
        self.up_prob = pool["up_prob"]          # 当期up
        self.fes_prob = pool["fes_prob"]        # 当期FES
        self.s3_prob = pool["s3_prob"]
        self.s2_prob = pool["s2_prob"]
        self.s1_prob = 1000 - self.s2_prob - self.s3_prob
        self.up = pool["up"]
        self.fes = pool["fes"]                  # 当期Fes
        self.star3 = pool["star3"]
        self.star2 = pool["star2"]
        self.star1 = pool["star1"]


    def gacha_one(self, ten_flag:bool = False):
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
        if self.s1_prob is None:
            self.s1_prob = 1000 - self.s3_prob - self.s2_prob
        total_ = self.s3_prob + self.s2_prob + self.s1_prob
        pick = random.randint(1, total_)
        
        if pick <= self.up_prob:
            return Chara.fromname(random.choice(self.up), 3), 100
        elif pick <= self.up_prob + self.fes_prob:   # fes
            return Chara.fromname(random.choice(self.fes), 3), 50
        elif pick <= self.s3_prob:
            return Chara.fromname(random.choice(self.star3), 3), 50
        elif (pick <= self.s2_prob + self.s3_prob) or (ten_flag == True):
            return Chara.fromname(random.choice(self.star2), 2), 10
        else:
            return Chara.fromname(random.choice(self.star1), 1), 1


    def gacha_ten(self):
        result = []
        hiishi = 0
        up = self.up_prob
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2
        for _ in range(9):    # 前9连
            c, y = self.gacha_one(False)
            result.append(c)
            hiishi += y
        c, y = self.gacha_one(True)    # 保底第10抽
        result.append(c)
        hiishi += y

        return result, hiishi


    def gacha_tenjou(self):
        result = {'up': [], 's3': [], 's2':[], 's1':[]}
        first_up_pos = 999999
        up = self.up_prob
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2
        for i in range(30):
            # 前9抽
            # print("\n", i * 10, "-", i * 10 + 10)
            for k in range(9):
                c, y = self.gacha_one(False)
                if 100 == y:
                    result['up'].append(c)
                    first_up_pos = min(first_up_pos, i * 10 + k)
                elif 50 == y:
                    result['s3'].append(c)
                elif 10 == y:
                    result['s2'].append(c)
                elif 1 == y:
                    result['s1'].append(c)
                else:
                    pass    # should never reach here
            # 第10抽保底
            c, y = self.gacha_one(True)
            if 100 == y:
                result['up'].append(c)
                first_up_pos = min(first_up_pos, 10 * (i + 1))
            elif 50 == y:
                result['s3'].append(c)
            elif 10 == y:
                result['s2'].append(c)
            else:
                pass    # should never reach here
        result['first_up_pos'] = first_up_pos
        return result
