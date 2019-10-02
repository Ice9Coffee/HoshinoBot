from os import path
import json
import random

class Gacha(object):

    def __init__(self):
        super().__init__()
        self.load_pool()


    def load_pool(self):
        config_file = path.join(path.dirname(__file__), "config.json")
        with open(config_file) as f:
            config = json.load(f)
            pool = config["GACHA_POOL"]
            self.up_prob = pool["up_prob"]
            self.s3_prob = pool["s3_prob"]
            self.s2_prob = pool["s2_prob"]
            self.s1_prob = 1000 - self.s2_prob - self.s3_prob
            self.up = pool["up"]
            self.star3 = pool["star3"]
            self.star2 = pool["star2"]
            self.star1 = pool["star1"]


    def gacha_one(self, up_prob:int, s3_prob:int, s2_prob:int, s1_prob:int=None):
        '''
        sx_prob: x星概率，要求和为1000
        up_prob: UP角色概率（从3星划出）
        up_chara: UP角色名列表

        return: (单抽角色名, 秘石数)
        ---------------------------
        |up|      |  20  |   78   |
        |   ***   |  **  |    *   |
        ---------------------------
        '''
        if s1_prob is None:
            s1_prob = 1000 - s3_prob - s2_prob
        total_ = s3_prob + s2_prob + s1_prob
        pick = random.randint(1, total_)
        if pick <= up_prob:
            return random.choice(self.up), 100
        elif pick <= s3_prob:
            return random.choice(self.star3), 50
        elif pick <= s2_prob + s3_prob:
            return random.choice(self.star2), 10 
        else:
            return random.choice(self.star1), 1


    def gacha_10(self):
        result = []
        hiishi = 0
        up = self.up_prob
        s3 = self.s3_prob
        s2 = self.s2_prob
        s1 = 1000 - s3 - s2        
        for _ in range(9):    # 前9连
            x, y = self.gacha_one(up, s3, s2, s1)
            result.append(x)
            hiishi = hiishi + y
        x, y = self.gacha_one(up, s3, s2 + s1, 0)    # 保底第10抽
        result.append(x)
        hiishi = hiishi + y

        return result, hiishi
