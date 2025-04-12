#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="/opt/AttendanceManager"

# 必要なディレクトリの作成
echo "Creating directories..."
sudo mkdir -p "${BASE_DIR}/scripts"
sudo mkdir -p "${BASE_DIR}/logs"

# 権限の設定
echo "Setting permissions..."
sudo chown -R $USER:$USER "${BASE_DIR}"

# スクリプトのコピーと実行権限の付与
echo "Copying and setting up scripts..."
sudo cp "${SCRIPT_DIR}/check_coretime.sh" "${BASE_DIR}/scripts/"
sudo chmod +x "${BASE_DIR}/scripts/check_coretime.sh"

# crontabの設定
echo "Setting up crontab..."
(crontab -l 2>/dev/null; cat << 'EOF'
# 月曜から金曜のコアタイムチェック（ログ付き）
0 9 15 * * 1-5 /opt/AttendanceManager/scripts/check_coretime.sh 1 >> /opt/AttendanceManager/logs/coretime.log 2>&1
0 11 0 * * 1-5 /opt/AttendanceManager/scripts/check_coretime.sh 2 >> /opt/AttendanceManager/logs/coretime.log 2>&1
30 13 30 * * 1-5 /opt/AttendanceManager/scripts/check_coretime.sh 3 >> /opt/AttendanceManager/logs/coretime.log 2>&1
15 15 15 * * 1-5 /opt/AttendanceManager/scripts/check_coretime.sh 4 >> /opt/AttendanceManager/logs/coretime.log 2>&1
0 16 0 * * 1-5 /opt/AttendanceManager/scripts/check_coretime.sh 5 >> /opt/AttendanceManager/logs/coretime.log 2>&1
EOF
) | crontab -

echo "Setup completed successfully!"
echo "Please check the following:"
echo "1. Directories created at: ${BASE_DIR}"
echo "2. Scripts installed at: ${BASE_DIR}/scripts"
echo "3. Logs will be written to: ${BASE_DIR}/logs"
echo "4. Crontab has been updated" 