#!/bin/bash
python3 makeuser.py &
python3 botnoly.py -t $1 -k $2 &
python3 emailtobot.py -t $1 &