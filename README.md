# EmailToBot

##### docker 启动

替换*号内容，依次为，机器人token，确认密钥，邮箱用户名，用户密码

例如：

```
FROM python:3

WORKDIR /usr/src/app

COPY emailtobot.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "./emailtobot.py", "-t" , "*:*", "-k", "*", "-u", "*@*.com", "-p", "*"]
```

##### example

```
docker build -t etb .
docker run -p 18025:18025 -d etb
```

该项目用于部署telegram bot机器人接收本地邮件内容，新建一个telegram机器人这里不详细描述。并且本项目支持docker部署。
