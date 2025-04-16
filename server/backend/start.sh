#!/bin/bash

# cronサービスを起動
service cron start

# ログファイルの権限を設定
touch /var/log/cron.log
chmod 666 /var/log/cron.log

# FastAPIアプリケーションを起動
cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 