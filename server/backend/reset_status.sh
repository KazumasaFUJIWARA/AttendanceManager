#!/bin/bash

# ログ出力開始
echo "[START] $(date)" >> /var/log/cron.log
echo "" >> /var/log/cron.log

# 引数チェック
NUM="$1"
if [ -z "$NUM" ]; then
  echo "[ERROR] 引数 NUM が必要です" >> /var/log/cron.log
  exit 1
fi

# 環境変数の読み込み
export $(xargs < /etc/cron.env)

# API 呼び出し
curl -X POST http://${ATTEND_SERVER}/api/reset-status >> /var/log/cron.log 2>&1

# ログ出力終了
echo "" >> /var/log/cron.log
echo "[END] $(date)" >> /var/log/cron.log
echo "" >> /var/log/cron.log
