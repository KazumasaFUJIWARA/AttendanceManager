# プロジェクトルート直下の Dockerfile
FROM debian:bullseye

# 作業ディレクトリを /app に設定
WORKDIR /app

# backend と public ディレクトリをコピー
COPY backend /app/backend
COPY public /app/public
COPY opt/check_coretime.sh /app/check_coretime.sh

# cronのインストール
RUN apt-get update && \
    apt-get install -y cron python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

# Pythonの依存パッケージをインストール
RUN pip3 install -r backend/requirements.txt

# cronの設定
COPY backend/crontab /etc/cron.d/app-cron
RUN echo "" >> /etc/cron.d/app-cron && \
    chmod 0644 /etc/cron.d/app-cron && \
    crontab /etc/cron.d/app-cron

# ログファイルを作成
RUN touch /var/log/cron.log

# 起動スクリプトをコピーして実行権限を付与
COPY backend/start.sh /app/start.sh
RUN chmod +x /app/start.sh
RUN chmod +x /app/check_coretime.sh

# コンテナ外部に公開するポート番号（FastAPI アプリ用）
EXPOSE 8000

# 起動スクリプトを実行
CMD ["/app/start.sh"]
