#!/bin/bash
# shellcheck disable=SC2164
cd ../run/
gunicorn sis_main_process:app -c sis_gunicorn.py
gunicorn_pid=$(ps aux | grep 'gunicorn' | grep -v 'grep' | awk '{print $2}')
lsof -i:23333
echo 'server is running, pid is '"$gunicorn_pid"