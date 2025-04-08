FROM python:3.9-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# アプリケーションを実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 