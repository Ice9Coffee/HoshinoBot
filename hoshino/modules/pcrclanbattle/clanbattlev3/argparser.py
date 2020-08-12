from typing import Dict, List

from .exception import ParseError


class ArgHolder:
    __slots__ = ("type", "default", "tip")

    def __init__(self, tip, type_=str, default=None):
        self.type = type_
        self.default = default
        self.tip = tip


class ArgParser:
    def __init__(self, arg_dict=None):
        self.arg_dict: Dict[str, ArgHolder] = arg_dict or {}

    def add_arg(self, prompt, tip, type_=str, default=None):
        self.arg_dict[prompt] = ArgHolder(tip, type_, default)

    def parse(self, args: List[str]) -> dict:
        result = {}

        # 解析参数，以一个字符开头，或无前缀
        for arg in args:
            prompt, x = arg[0].upper(), arg[1:]
            if prompt in self.arg_dict:
                holder = self.arg_dict[prompt]
            elif "" in self.arg_dict:
                holder = self.arg_dict[""]
                prompt, x = "", arg
            else:
                raise ParseError(f"未知参数：{arg}")

            try:
                result.setdefault(prompt, holder.type(x))  # 多个参数只取第1个
            except ParseError:
                raise
            except Exception:
                raise ParseError(f"解析{holder.tip}失败")

        # 检查所有参数是否以赋值
        for prompt, holder in self.arg_dict.items():
            if prompt not in result:
                if holder.default is None:  # 缺失必要参数 抛异常
                    msg = f"缺少参数：{holder.tip}"
                    raise ParseError(msg)
                else:
                    result[prompt] = holder.default

        return result
