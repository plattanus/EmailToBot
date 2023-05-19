FROM python:3

WORKDIR /usr/src/app

COPY emailtobot.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "./emailtobot.py", "-t" , "*:*", "-k", "*", "-u", "*@*.com", "-p", "*"]

