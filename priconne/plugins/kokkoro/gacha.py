import random

class Gacha(object):

    up_prob =  28
    s3_prob = 100
    s2_prob = 200

    up = ['蕾姆', '爱蜜莉雅', '跳跃王', '镜华(万圣节)']

    # 这里仅填3星常驻角色。不要填UP角否则出率会偏高
    star3 = [
        '杏奈','真步','璃乃','初音','霞','伊绪',
        '咲恋','望','妮诺','秋乃','镜华','智','真琴',
        '伊莉亚','纯','静流','莫妮卡','流夏','吉塔',
        '亚里莎','安','古蕾娅', '空花(大江户)', '妮诺(大江户)',
        '华哥', '生菜']

    star2 = [
        '茉莉','茜里','宫子','雪','七七香','美里',
        '铃奈','香织','美美','绫音','铃','惠理子',
        '忍','真阳','栞','千歌','空花','珠希','美冬',
        '深月','纺希']

    star1 = [
        '日和','优衣','怜','禊','胡桃','依里','铃莓',
        '优花梨','碧','美咲','莉玛','步未']

    fes = ['克里丝提娜','矛依未']


    @staticmethod
    def gacha_one(up_prob:int, s3_prob:int, s2_prob:int, s1_prob:int=None):
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
            return random.choice(Gacha.up), 100
        elif pick <= s3_prob:
            return random.choice(Gacha.star3), 50
        elif pick <= s2_prob + s3_prob:
            return random.choice(Gacha.star2), 10 
        else:
            return random.choice(Gacha.star1), 1


    @staticmethod
    def gacha_10():
        result = []
        hiishi = 0
        up = Gacha.up_prob
        s3 = Gacha.s3_prob
        s2 = Gacha.s2_prob
        s1 = 1000 - s3 - s2        
        for _ in range(9):    # 前9连
            x, y = Gacha.gacha_one(up, s3, s2, s1)
            result.append(x)
            hiishi = hiishi + y
        x, y = Gacha.gacha_one(up, s3, s2 + s1, 0)    # 保底第10抽
        result.append(x)
        hiishi = hiishi + y

        return result, hiishi
