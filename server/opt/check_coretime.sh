#!/bin/bash

# 環境変数の設定
export PYTHONPATH=/opt/AttendanceManager/server/backend

# コアタイムチェックの実行
cd /opt/AttendanceManager/scripts
python3 -c "
import requests
import datetime

def check_coretime(check_number):
    try:
        response = requests.post(f'http://localhost:8000/core-time/check/{check_number}')
        print(f'[{datetime.datetime.now()}] Core-time check {check_number}: {response.status_code}')
    except Exception as e:
        print(f'[{datetime.datetime.now()}] Error in core-time check {check_number}: {str(e)}')

check_coretime($1)
" 