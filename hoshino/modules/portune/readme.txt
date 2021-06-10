
安装方法：

①将‘portune’文件夹复制到hoshino\modules文件夹下；

②打开portune文件夹下的portune.py，按照注释选择编辑：
    1.帮助文本
    2.每日抽签次数

③将‘portunedata’文件夹复制到hoshino的资源文件夹res\img文件夹下；

④最后记得在hoshino\config\__bot__.py的‘MODULES_ON’中加上‘portune’


##################################################
portune是从xcwbot上的vortune模块修改而来的，感谢原代码作者fz6m
项目地址：https://github.com/fz6m/nonebot-plugin

感谢zzbslayer对代码的重构
项目地址：https://github.com/zzbslayer/KokkoroBot-Multi-Platform
##################################################

======change log=======
1.增加一波新角色

2.改变读取方式，简化代码(zzbslayer)

3.转用base64发图，本地不再存储
