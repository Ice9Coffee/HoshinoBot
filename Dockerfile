FROM python:3.8
RUN mkdir -p /bot
WORKDIR /bot
COPY requirements.txt /bot/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
COPY . /bot
CMD ["python", "run.py"]