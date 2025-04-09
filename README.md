# 出席管理システム

## 概要
このプロジェクトは、学生の出席状況を管理するためのWebアプリケーションです。リアルタイムでの出席記録、コアタイム管理、アラート機能を提供します。

## 主な機能
- 学生の出席記録（入室・退室）
- コアタイム管理（8:30-17:30）
- リアルタイムの出席状況表示
- アラート機能（コアタイム違反、長時間滞在）
- 出席履歴の確認
- 学生情報の管理

## 技術スタック
- バックエンド: FastAPI (Python)
- フロントエンド: HTML, CSS, JavaScript
- データベース: SQLite
- コンテナ化: Docker

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/KazumasaFUJIWARA/AttendanceManager.git
cd AttendanceManager
```

### 2. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定します：
```
DATABASE_URL=sqlite:///./attendance.db
```

### 3. Docker環境の構築
```bash
docker-compose up -d
```

### 4. アプリケーションの起動
サーバーが自動的に起動し、以下のURLでアクセス可能になります：
- API: http://localhost:8889
- Swagger UI: http://localhost:8889/docs
- フロントエンド: http://localhost:8889/index.html

## API エンドポイント

### 学生管理
- `POST /api/students/` - 学生の登録
- `GET /api/students/{student_id}` - 学生情報の取得
- `GET /api/students/` - 全学生の一覧取得

### 出席管理
- `POST /api/attendance/` - 出席記録の作成
- `GET /api/attendance/{student_id}` - 学生の出席履歴取得
- `GET /api/attendance/current/{student_id}` - 現在の出席状況取得

### コアタイム管理
- `GET /api/core-time/` - コアタイム情報の取得
- `GET /api/core-time/violations/` - コアタイム違反の一覧取得

### アラート
- `GET /api/alerts/` - アラート一覧の取得

## フロントエンド機能
- リアルタイムの出席状況表示
- 学生の入室・退室記録
- 出席履歴の表示
- コアタイム違反の表示
- アラート通知

## 開発環境
- Python 3.8以上
- Docker
- Docker Compose

## ライセンス
MIT License

## 作者
Kazumasa FUJIWARA
