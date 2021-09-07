from typing import List, Dict
from nonebot import Message
from hoshino.util import filt_message

from ..exception import *


class ArgHolder:
    __slots__ = ('type', 'default', 'tip')
    def __init__(self, type=str, default=None, tip=None):
        self.type = type
        self.default = default
        self.tip = tip


class ParseResult(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, value):
        self[key] = value


class ArgParser:
    def __init__(self, usage, arg_dict=None):
        self.usage = f"【用法/用例】\n{usage}\n\n※无需输入尖括号，圆括号内为可选参数，用空格隔开命令与参数"
        self.arg_dict: Dict[str, ArgHolder] = arg_dict or {}


    def add_arg(self, name, *, type=str, default=None, tip=None):
        self.arg_dict[name] = ArgHolder(type, default, tip)


    def parse(self, args: List[str], message: Message) -> ParseResult:
        result = ParseResult()

        # 解析参数，以一个字符开头，或无前缀
        for arg in args:
            name, x = arg[0].upper(), arg[1:]
            if name in self.arg_dict:
                holder = self.arg_dict[name]
            elif '' in self.arg_dict:
                holder = self.arg_dict['']
                name, x = '', arg
            else:
                raise ParseError('命令含有未知参数', self.usage)

            try:
                if holder.type == str:
                    result.setdefault(name, filt_message(holder.type(x)))
                else:
                    result.setdefault(name, holder.type(x))     # 多个参数只取第1个
            except ParseError as e:
                e.append(self.usage)
                raise e
            except Exception:
                msg = f"请给出正确的{holder.tip or '参数'}"
                if name:
                    msg += f"以{name}开头"
                raise ParseError(msg, self.usage)

        # 检查所有参数是否以赋值
        for name, holder in self.arg_dict.items():
            if name not in result:
                if holder.default is None:  # 缺失必要参数 抛异常
                    msg = f"请给出{holder.tip or '缺少的参数'}"
                    if name:
                        msg += f"以{name}开头"
                    raise ParseError(msg, self.usage)
                else:
                    result[name] = holder.default

        # 解析Message内的at
        result['at'] = 0
        for seg in message:
            if seg.type == 'at':
                result['at'] = int(seg.data['qq'])

        return result
