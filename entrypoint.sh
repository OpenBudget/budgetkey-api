#!/bin/sh

python prepare.py
/usr/local/bin/gunicorn -w 8 --bind 0.0.0.0:5000 server:app