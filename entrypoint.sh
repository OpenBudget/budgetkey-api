#!/bin/sh

python prepare.py
/usr/local/bin/gunicorn -w 16 --timeout $TIMEOUT --bind 0.0.0.0:$PORT --log-level debug server:app