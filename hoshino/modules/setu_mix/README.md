# setu_mix

基于HoshinoBot v2的涩图插件, 从 [acg-gov.com](https://acg-gov.com) 和 [lolicon.app](https://lolicon.app/) 获取图片.

本项目地址 https://github.com/zyujs/setu_mix

## 注意事项

本插件图片存放位置为 `RES_DIR/setu_mix` , 使用前请保证HoshinoBot的 `RES_DIR` 已经正确配置.

刚开始使用插件时本地仓库为空, 会导致无法发送随机图片, 可以在安装配置完毕后使用 `setu fetch` 命令手动抓取一批图片.

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/zyujs/setu_mix.git`
1. 将本插件目录下的配置文件模板 `config.template.json` 复制为 `config.json` , 修改该配置文件设置自己的apikey和其他选项, 除apikey以外都可保持默认值.
1. 在 `config/__bot__.py`的模块列表里加入 `setu_mix`
1. 重启HoshinoBot

## 配置说明

- `apikey` : apikey, 必填.
- `mode` : 模块模式, 0=关闭, 1=在线(不使用本地仓库), 2=在线(使用本地仓库), 3=离线(仅使用本地仓库), 默认模式为2.

## 指令说明

- `涩图` : 随机获取1张图片
- `来n张涩图` : 随机获取n张图片
- `搜涩图 keyword` : 搜索指定关键字的图片
- `搜n张涩图 keyword` : 搜索n张指定关键字的图片
- `本日涩图排行榜 [page]` : 获取p站排行榜
- `看涩图 [n]` : 获取p站排行榜指定排名的图片
- `看涩图 start end` : 获取p站排行榜排名从start到end的全部图片

注:排行榜相关功能需要开启acggov模块

### 以下指令仅限超级用户使用

- `setu set 模块 设置值 [群号]` : 修改本群或指定群的设置, 以下为设置项 - 取值 - 说明:
  - `acggov` : `on / off` 是否开启acggov模块
  - `lolicon` : `on / off` 是否开启lolicon模块
  - `lolicon_r18` : `on / off` 是否开启lolicon_r18模块
  - `withdraw` : `n` 发出的图片在n秒后撤回,设置为0表示不撤回. 如果撤回功能异常, 请关闭bot宿主程序的分片发送功能.
  - `xml` : `on / off` (仅支持go-cqhttp)使用cardimage卡片模式发送图片, 注意xml类消息容易触发风控且不支持某些客户端.
- `setu get [群号]` : 查看本群或指定群的模块开启状态
- `setu fetch` :  手动从api拉取一批图片存入本地仓库(插件每半小时会自动拉取一次)
- `setu warehouse` : 查询本地仓库图片数量

## 开源

本插件以AGPL-v3协议开源
