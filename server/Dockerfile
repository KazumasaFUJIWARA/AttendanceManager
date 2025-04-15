# プロジェクトルート直下の Dockerfile
FROM debian:bullseye

# 作業ディレクトリを /app に設定
WORKDIR /app

# backend と public ディレクトリをコピー
COPY backend /app/backend
COPY public /app/public

# cronのインストール
RUN apt-get update && \
    apt-get install -y cron python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Pythonの依存パッケージをインストール
RUN pip3 install -r backend/requirements.txt

# cronの設定
RUN echo "* * * * * date >> /var/log/cron.log 2>&1" > /etc/cron.d/app-cron && \
    echo "0 0 * * * echo '' > /var/log/cron.log" >> /etc/cron.d/app-cron && \
    chmod 0644 /etc/cron.d/app-cron && \
    crontab /etc/cron.d/app-cron

# ログファイルを作成
RUN touch /var/log/cron.log

# 起動スクリプトをコピーして実行権限を付与
COPY backend/start.sh /start.sh
RUN chmod +x /start.sh

# コンテナ外部に公開するポート番号（FastAPI アプリ用）
EXPOSE 8000

# 起動スクリプトを実行
CMD ["/start.sh"]
