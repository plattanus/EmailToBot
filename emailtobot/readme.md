# EmailToBot

##### 1

```
python3 makeuser.py
```

##### 2

```
python3 botnoly.py -t '*:*' -k '*'
```

##### 3

```
python3 emailtobot.py -t '*:*'
```

background：debian11 python3.9

```
pip install aiosmtpd pyTelegramBotAPI dnspython python-telegram-bot argon2-cffi
```

##### run

```
chmod +x run.sh
./run.sh '*:*' '*'
```

##### stop

```
ps aux | grep python
kill PID
```
