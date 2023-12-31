# EmailToBot

This project automatically forwards mail that passes through the mail port of the local port to the telegram bot.
A new telegram robot will not be described in detail here.
Note: test.py is used to simulate sending mail for testing.

On-premises Deployment

```shell
$ python emailtobot.py -t
```

Docker Deployment

```dockerfile
FROM python:3
WORKDIR /usr/src/app
COPY emailtobot.py ./
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "./emailtobot.py", "-t" , <your_token>, "-k", <your_key>, "-u", <your_username>, "-p", <your_password>, "-P", <your_port>]
```

Start Container

```bash
$ docker build -t etb .
$ docker run -p <bind_port>:<your_port> -d etb
```
