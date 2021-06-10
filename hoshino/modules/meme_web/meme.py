import os
import nonebot
from quart import request, session, redirect, Blueprint, url_for, render_template, jsonify, session
from nonebot.exceptions import CQHttpError
from pathlib import Path
from hoshino import R, Service, priv, config
from hoshino.util import DailyNumberLimiter

public_address = config.IP  # 修改为服务器公网ip
meManagePwd = '31894267'  # 删除文件密码
loginUserName = '菜如狗怎么了'  # 登录账户
loginPassword = '31894267'  # 登录密码
bot_name = '菜狗'  # 机器人名字
group_name = '测试'  # 公会名

sv_help = '''
- [表情列表] 查看目前有哪些表情
- [生成表情 表情名字 文案] 生成一张表情包
- [查看表情 XXX] XXX是表情名字,要准确
- [查看XX表情] XX是表情名字的关键词,支持模糊搜索
- [删除表情 XX] XX是表情名字
- [上传表情 表情名字 图片] 上传一张表情
'''.strip()

sv = Service(
    name='表情包生成',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-表情包生成"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


work_env = Path(os.path.dirname(__file__))
meme_folder = work_env.joinpath('meme')
static_folder = work_env.joinpath('static')
me = Blueprint('me', __name__, template_folder='templates', static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(meme_folder)


@sv.on_rex('^查看.{0,}表情$')
async def meme_query(bot, ev):
    uid = ev.user_id
    # 文件查找
    arv = ev.message.extract_plain_text()
    l = len(arv)
    arv = arv[2:l - 2]
    msg = ''
    for path in meme_folder.iterdir():
        if path.name.find(arv) >= 0:
            msg += f'[CQ:image,file=file:///{path.as_posix()}]'
    if msg == '':
        await bot.send(ev, f'没有找到{arv}表情！', at_sender=True)
        return
    await bot.send(ev, msg)


ALLOWED_EXTENSIONS = set(['png', 'jpg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@me.route('/uploader', methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':
        file = await request.files
        file = file['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(meme_folder.joinpath(filename).as_posix())
            return 'success'
        return 'failed'


@me.route('/meme')
async def index():
    if not session.get('username'):
        return redirect(url_for("me.web_login"))
    return await render_template('manage.html', bot_name=bot_name, group_name=group_name)


@me.route('/meme/login', methods=['GET', 'POST'])
async def web_login():
    if request.method == 'GET':
        return await render_template('login.html', bot_name=bot_name)
    elif request.method == 'POST':
        username = request.args.get("username")
        password = request.args.get("password")
        if username == loginUserName and password == loginPassword:
            session['username'] = username
            return 'success'
        return 'failed'


@me.route("/del", methods=['DELETE'])
async def del_file():
    filename = request.args.get('filename')
    pwd = request.args.get('password')
    if pwd != meManagePwd:
        return 'wrong password'
    file_dir = meme_folder.joinpath(filename)
    if file_dir.exists():
        file_dir.unlink()
        return 'success'
    return 'error'


@me.route('/get/memelist')
async def get_meme_list():
    meme_list = []
    for path in meme_folder.iterdir():
        if allowed_file(path.name):
            meme_list.append({'filename': path.name, 'size': path.stat().st_size})
    return jsonify(meme_list)


@sv.on_fullmatch("表情管理", only_to_me=True)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev, f'http://{public_address}:{cfg.PORT}/meme')
