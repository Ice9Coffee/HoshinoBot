#coding=utf-8
import jieba
import pandas as pd
import pinyin



def create_cut(text):
    return " ".join(jieba.cut(text, cut_all=False))


def text_to_emoji(text, method=1):
    # 默认轻度抽象
    if method == 0:
        text_jieba = jieba.cut(text, cut_all=False)
        print(text_jieba)
        text_with_emoji = ''

        for word in text_jieba:
            word = word.strip()
            if word in bible_light_dict.keys():
                text_with_emoji += bible_light_dict[word]
            else:
                if len(word) > 0:#不止一个字
                    for character in word:
                        if character in bible_light_dict.keys():
                            text_with_emoji += bible_light_dict[character]
                        else:
                            text_with_emoji += character
                else: # 一个字
                    text_with_emoji += word

        return text_with_emoji
    elif method == 1:
        text_with_emoji = ''
        # 首先还是分词
        # 分词检索
        # 分词拼音检索
        # 单字检索
        # 单字拼音检索
        text_jieba = jieba.cut(text, cut_all=False)
        for word in text_jieba:
            word = word.strip()
            # 分词检索
            if word in bible_light_raw:
                text_with_emoji += bible_light_dict[word]
            elif word not in bible_light_raw:
                word_py = pinyin.get(word, format="strip")
                # 分词拼音检索
                if word_py in bible_deep_dict.keys():
                    text_with_emoji += bible_deep_dict[word_py]
                else:
                    if len(word) > 0: # if the two characters or more
                        # 单字检索
                        for character in word:
                            if character in bible_light_dict.keys():
                                text_with_emoji += bible_light_dict[character]
                            else:
                                # 单字拼音检索
                                character_py = pinyin.get(character, format="strip")
                                if character_py in bible_deep_dict.keys():
                                    text_with_emoji += bible_deep_dict[character_py]
                                else:
                                    text_with_emoji += character
                    else: # 只有一个汉字，前面已经检测过字和拼音都不在抽象词典中，直接加词
                        text_with_emoji += word.strip()
        return text_with_emoji
bible_light = pd.read_excel('./hoshino/modules/nmsl/data/bible_new.xlsx')
bible_light_raw = bible_light['raw'].values
bible_light_cx = bible_light['chouxiang'].values
bible_light_dict = {}
bible_deep_dict = {}
for bl_r, bl_cx in zip(bible_light_raw, bible_light_cx):
    bible_light_dict[bl_r] = bl_cx
    # if bl_r not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
    if bl_r not in range(11):
        bl_r_py = pinyin.get(bl_r, format='strip')
    else:
        bl_r_py = bl_r
    bible_deep_dict[bl_r_py] = bl_cx

if __name__ == '__main__':
    print(text_to_emoji('我质疑宁妈死了'))
