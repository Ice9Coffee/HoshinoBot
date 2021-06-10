# 表情包生成器 For HoshinoV2

本插件修改自[fz6m](https://github.com/fz6m/)所编写的的NoneBot插件[CQimage](https://github.com/fz6m/nonebot-plugin/tree/master/CQimage), 对HoshinoBotV2进行了适配并做了些微改动. 

## 开始使用

1. 在HoshinoBot的modules目录下克隆本项目:
    ```
    git clone https://github.com/pcrbot/image-generate.git`
    ```
2. 安装依赖, 如下载过慢建议清华镜像, 一般来说只要你成功安装了HoshinoBot便可以略过此步:
    ```
   pip install -r ./requirements.txt
    ```
3. 将`image-generate`文件夹移动至HoshinoBot的`res/img/`目录下,正确的目录结构:
   ```
   res
   |--img
       |--image-generate
           |--image_data
           |--image
   ```


4. 在`config/__bot__.py`文件中的`MODULES_ON`里添加一行`'image-generate'`,以启用本插件

5. 如果出现字体缺失的情况,请自行安装目录下ttf格式的字体

## 指令示例

* 表情包帮助  |  imghelp:
        
        查看本插件的使用帮助
* 选图猫猫  |  imgsw 栞栞:
 
        选择生成表情包所用的底图
* 选图列表  |  imgswl:  
  
        查看能选择的底图列表,<>内的数字为必选数字
* HelloWorld.jpg  |  生成表情包我要白丝!  |  imgen 诶嘿嘿:   
    
        将`.jpg`前的文字或`生成表情包`后的文字做为内容
        生成当前所选底图所对应的表情包

## 自定义表情包

用户是不可以自定义新表情包的，因为文字位置用户不能控制，必须由我们先定义好表情配置才能提供给用户使用。
流程如下：

### 建立文件夹

在 `image_data/` 下建立一个由你决定的为 表情id 的文件夹，假设为 `katsuna` ，此时路径为 `image_data/katsuna/` 。

### 定义表情

一张表情拥有一个独立的文件夹，在 `katsuna/` 下建立一个表情配置文件 `config.ini`  ，来配置我们的表情，参数说明与格式如下：

|  参数  |  说明  |
|  ----  |  ----  |
|  name  |  表情图文件名，且必须与文件夹名相同  |
|  font_max  |  表情图内添加文字可能的最大长度  |
|  font_size  |  表情图内添加文字的尺寸，一般为40，小图30，大图50  |
|  font_center_x  |  表情图内添加文字的中心点x位  |
|  font_center_y  |  表情图内添加文字的中心点y位（由上至下）  |
|  color  |  表情图内添加文字的颜色，一般为black/white  |
|  font_sub  |  控制文字大小衰减的档位，一般为5  |

格式：
```
{
        "name":"", 
        "font_max":,
        "font_size":, 
        "font_center_x":, 
        "font_center_y":, 
        "color":"",
        "font_sub":
}

```
例子：
```
{
        "name":"katsuna",
        "font_max":230,
        "font_size":35,
        "font_center_x":125,
        "font_center_y":278,
        "color":"black",
        "font_sub":5
}
```

### 添加别名

在 `image_data/bieming/name.ini` 中，添加一行如下格式的别名标识：

    用户使用的别名 表情id

例子：

    kora katsuna
那么下次用户发送 `选图kora` ，就会更换到这个新的表情底图。

>**三个一样**<br>
必须注意的是， `表情id` 不光是文件夹的名字，也是配置文件中 `name` 属性的值，也与提供给用户别名切换文件中的 **第二个** 参数相同。

## 设定表情配置的一种快捷方法
![avatar](https://fz6m.github.io/plugin-press/guide_image.jpg)