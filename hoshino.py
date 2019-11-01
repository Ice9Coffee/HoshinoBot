from os import path
import nonebot

import config

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'priconne', 'plugins'),
        'priconne.plugins'
    )
    # nonebot.load_plugins(
    #     path.join(path.dirname(__file__), 'translate', 'plugins'),
    #     'translate.plugins'
    # )
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'groupmaster', 'plugins'),
        'groupmaster.plugins'
    )
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'subscribe', 'plugins'),
        'subscribe.plugins'
    )
    nonebot.run()
