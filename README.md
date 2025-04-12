# 出席管理システム

## 概要
このシステムは、学生の出席状況を管理し、コアタイムの遵守状況を監視するためのWebアプリケーションです。

## 機能
- 学生の入退室管理
- コアタイム設定と監視
- 出席履歴の記録と表示
- コアタイム違反の検出と通知
- Telegram通知機能（入退室時の自動通知）

## APIエンドポイント

### 学生管理API
- `POST /api/students/` - 新規学生の登録
  - 入力: `{"student_id": "string", "name": "string"}`
  - 出力: 登録された学生情報（ID、名前）
- `GET /api/students/` - 全学生の一覧取得
  - 出力: 学生情報の配列 `[{"student_id": "string", "name": "string", ...}]`
- `GET /api/students/{student_id}` - 特定の学生の情報取得
  - 出力: 学生情報 `{"student_id": "string", "name": "string", ...}`

### 入退室管理API
- `POST /api/attendance/` - 入退室記録の登録
  - 入力: `{"student_id": "string", "time": "datetime"}`
  - 出力: `{"name": "string", "status": "入室" | "退室"}`
- `GET /api/attendance/{student_id}` - 特定の学生の出席履歴取得
  - クエリパラメータ: `days` (オプション) - 過去何日分の履歴を取得するか
  - 出力: 出席記録の配列 `[{"student_id": "string", "entry_time": "datetime", "exit_time": "datetime"}]`
- `GET /api/current-status/` - 現在の入室状況一覧取得
  - 出力: 入室状況の配列 `[{"student_id": "string", "entry_time": "datetime"}]`
- `POST /api/attendance-now/{student_id}` - 現在時刻での入退室記録
  - 出力: `{"name": "string", "status": "入室" | "退室"}`

### コアタイム管理API
- `GET /api/core-time/check/{period}` - 特定の時限のコアタイム遵守状況チェック
  - パラメータ: `period` (1-4) - チェックする時限
  - 出力: `{"violations": ["student_id1", "student_id2", ...]}`
  - 機能: コアタイム違反を検出すると、Telegramに自動通知を送信します
- `GET /api/core-time/violations` - コアタイム違反履歴の取得
  - 出力: アラートの配列 `[{"student_id": "string", "alert_date": "date", "alert_type": "string"}]`

### コアタイム設定API
- `POST /api/coretime/{student_id}` - 学生のコアタイム設定
  - 入力: 
    ```json
    {
      "core_time_1_day": integer,    // 1:月曜 2:火曜 3:水曜 4:木曜 5:金曜 6:土曜 7:日曜
      "core_time_1_period": integer, // 1:1限 2:2限 3:3限 4:4限
      "core_time_2_day": integer,    // 1:月曜 2:火曜 3:水曜 4:木曜 5:金曜 6:土曜 7:日曜
      "core_time_2_period": integer  // 1:1限 2:2限 3:3限 4:4限
    }
    ```
  - 出力: `{"status": "success", "message": "コアタイムを設定しました"}`
- `GET /api/coretime/{student_id}` - 学生のコアタイム設定取得
  - 出力: 
    ```json
    {
      "core_time_1_day": integer,    // 1:月曜 2:火曜 3:水曜 4:木曜 5:金曜 6:土曜 7:日曜
      "core_time_1_period": integer, // 1:1限 2:2限 3:3限 4:4限
      "core_time_2_day": integer,    // 1:月曜 2:火曜 3:水曜 4:木曜 5:金曜 6:土曜 7:日曜
      "core_time_2_period": integer  // 1:1限 2:2限 3:3限 4:4限
    }
    ```

## データベース
SQLiteデータベースを使用し、以下のテーブルを管理します：
- Student（学生情報）
  - student_id (PK)
  - name
  - core_time_1_day
  - core_time_1_period
  - core_time_2_day
  - core_time_2_period
  - core_time_violations
- AttendanceLog（出席記録）
  - id (PK)
  - student_id (FK)
  - entry_time
  - exit_time
- CurrentStatus（現在の入室状況）
  - student_id (PK)
  - entry_time
- Alert（コアタイム違反等のアラート）
  - id (PK)
  - student_id (FK)
  - alert_date
  - alert_period

## 開発環境
- Python 3.8以上
- FastAPI
- SQLAlchemy
- SQLite

## セットアップ
1. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

2. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定してください：
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

3. データベースの初期化
```bash
python init_db.py
```

4. サーバーの起動
```bash
uvicorn main:app --reload
```

## 注意事項
- 本番環境では適切なセキュリティ設定が必要です
- CORSの設定は開発環境用の設定となっています
- Telegram通知機能を使用する場合は、有効なボットトークンとチャットIDの設定が必要です

## フロントエンド機能
- リアルタイムの出席状況表示
- 学生の入室・退室記録
- 出席履歴の表示
- コアタイム違反の表示
- アラート通知

## フロントエンド実装詳細 (app.js)

### 概要
app.jsは出席管理システムのフロントエンド部分を担当するJavaScriptファイルです。学生の出席状況をリアルタイムで表示し、定期的にデータを更新します。

### 主要機能
- **自動データ更新**: ページ読み込み時にデータを取得し、1分ごとに自動更新
- **学生データ表示**: 学生ID、名前、現在の入室状況、今週の利用時間、コアタイム情報を表示
- **コアタイム管理**: 学生ごとのコアタイム情報（曜日と時限）を表示
- **エラーハンドリング**: データ取得失敗時のエラー表示と再読み込み機能

### API連携
- `/api/students/`: 学生一覧の取得
- `/api/current-status/`: 現在の入室状況の取得
- `/api/attendance/{student_id}?days=7`: 学生ごとの出席履歴（過去7日間）の取得

### 表示項目
1. **学生ID**: 学生の識別番号
2. **名前**: 学生の氏名
3. **入室状況**: 「入室中」または「退室中」を表示（リアルタイム更新）
4. **利用時間**: 今週の合計利用時間（時間単位で小数点1桁まで表示）
5. **コアタイム1**: 1つ目のコアタイム（曜日と時限）
6. **コアタイム2**: 2つ目のコアタイム（曜日と時限）
7. **違反回数**: コアタイム違反の回数（違反がある場合は強調表示）

### データ更新ロジック
1. 学生一覧を取得
2. 現在の入室状況を取得
3. 今週の日付範囲を計算（日曜日から現在まで）
4. 各学生について:
   - 現在の入室状況を確認
   - 今週の出席履歴を取得
   - 利用時間を計算（入室時間と退室時間の差分）
   - コアタイム情報を整形して表示

### エラー処理
- APIリクエスト失敗時: エラーメッセージを表示し、再読み込みボタンを提供
- 個別の学生データ取得失敗時: エラーをログに記録し、他の学生のデータ表示は継続

### 関数仕様

#### 1. `loadStudentData()`
- **目的**: 学生データを取得し、画面に表示する
- **戻り値**: なし（非同期関数）
- **処理内容**:
  1. 学生一覧をAPIから取得
  2. 現在の入室状況をAPIから取得
  3. 今週の日付範囲を計算（日曜日から現在まで）
  4. 各学生について:
     - 現在の入室状況を確認
     - 今週の出席履歴を取得
     - 利用時間を計算
     - コアタイム情報を整形
     - テーブル行を作成して表示
- **エラー処理**:
  - APIリクエスト失敗時: エラーメッセージを表示し、再読み込みボタンを提供
  - 個別の学生データ取得失敗時: エラーをログに記録し、他の学生のデータ表示は継続

#### 2. `formatCoreTime(day, period)`
- **目的**: コアタイムの曜日と時限を日本語表記に整形する
- **引数**:
  - `day`: 曜日を表す数値（0: 日曜日, 1: 月曜日, ..., 6: 土曜日）
  - `period`: 時限を表す数値（1: 1限, 2: 2限, ..., 6: 6限）
- **戻り値**: 整形されたコアタイム文字列（例: 「月曜1限」）または「-」（値がない場合）
- **処理内容**:
  1. 引数が無効な場合（null, undefined, 0）は「-」を返す
  2. 曜日と時限を日本語表記に変換して結合する

#### 3. イベントリスナー（DOMContentLoaded）
- **目的**: ページ読み込み時に初期データを取得し、定期的な更新を設定する
- **処理内容**:
  1. ページ読み込み時に`loadStudentData()`を実行
  2. 1分ごとに`loadStudentData()`を実行するタイマーを設定

### 定数
- **API_BASE_URL**: APIのベースURL（'/api'）
- **DAYS_OF_WEEK**: 曜日の日本語表記配列（['日', '月', '火', '水', '木', '金', '土']）
- **PERIODS**: 時限の日本語表記配列（['', '1限', '2限', '3限', '4限', '5限', '6限']）

## 開発環境
- Python 3.8以上
- Docker
- Docker Compose

## ライセンス
MIT License

## 作者
Kazumasa FUJIWARA
