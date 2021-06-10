import nonebot
from .view import switcher
app = nonebot.get_bot().server_app
app.register_blueprint(switcher)
