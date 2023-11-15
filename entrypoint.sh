#!/bin/sh

/usr/local/bin/gunicorn -w 8 --timeout 120 --bind 0.0.0.0:$PORT --log-level debug server:app