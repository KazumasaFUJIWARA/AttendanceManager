#!/bin/bash

# 環境変数の設定
export PYTHONPATH=/app/backend

# コアタイムチェックの実行
cd /app/backend
python3 -c "
import requests
import datetime

def check_coretime(check_number):
    try:
        response = requests.post(f'http://host.docker.internal:8889/api/core-time/check/{check_number}')
        print(f'[{datetime.datetime.now()}] Core-time check {check_number}: {response.status_code}')
    except Exception as e:
        print(f'[{datetime.datetime.now()}] Error in core-time check {check_number}: {str(e)}')

check_coretime($1)
" 