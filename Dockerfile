FROM python:3.8
RUN mkdir -p /bot
WORKDIR /bot
COPY requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
#RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
COPY ["fonts/Microsoft YaHei.ttf", "/usr/share/fonts/Microsoft YaHei.ttf"]