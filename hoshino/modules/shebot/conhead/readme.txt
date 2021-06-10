这是百度api接头+opencv接头二合一 , 其中opencv接头模块来自HOSHINO群文件《街头霸王-缝纫包》

安装说明：
1. 注册百度云账号，并开通人脸识别应用
2. 将得到的CLIENT_ID(API Key) CLIENT_SECRET(Secret Key)填入config.py
如果不使用api模式，可以跳过以上
3. 安装python的opencv库
切记： bot目录中一定不能出现中文，否则opencv读取会出现问题

指令：
接头1+图片——利用api接头
接头2+图片——利用opencv接头、
接头+图片——根据config里DEFAULT_MODE选择默认模式

两个模式优缺点：
baidu api： 对真人的准确度很好，但对动漫人脸识别度8太行，只有清晰正脸二次元图片才能识别,并且经常将其他部位识别为人脸，出现生草接头
opencv： 恰恰相反

api模式添加图片，参考data/head文件夹，修改dat.json，其中face_width为两眼最远距离(使用ps标工具)，angle为眼睛连线角度（代表头旋转的角度）,chin_tip_x(y)下巴
尖坐标（P快捷键F8）；见示意图。

							——by 倚栏待月