FROM python:3.10

WORKDIR /usr/src/app


COPY ./etb/emailtobot.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "./emailtobot.py", "-t" , "*:*", "-k", "*", "-u", "*@*.com", "-p", "*", "-P", "*"]

