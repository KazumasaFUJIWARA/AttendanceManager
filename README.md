# AttendanceManager

## 概要
学生の実習室の入退室の状況を、管理する為のシステムです。
学生証をFelicaリーダーで読み込み、Sharepoint上のリストにデータを送信します。
リストを経由して、現在の利用状況や、最近の利用状況のレポートを作成します。

## flow
### 実習室での操作
```mermaid
graph TD;
	INPUT["Felica 入力"]-->POST["Graph APIでリストに送信"]
	POST-->STATUS["入室か退室かの情報を取得し, 読み取りを行った通知を画面で表示する"]
```

### 実習室から利用するapi
```mermaid
graph TD;
	INPUT2["学籍番号と時刻を取得"] --> REC["EVENTリストに学籍番号と時刻を追加"]
	REC-->UPD{"CURRENTリストの対応する学籍番号の値を操作"}
	UPD-->|入室時刻が空|UPD1["入室時刻に入力時刻を入れる"]
	UPD1-->NAME["ROSTERリストから学籍番号に対応する氏名を取得"]
	NAME-->OUT["jsonでname:名前, status:入室を返す"]
	UPD-->|入室時刻が空でない|UPD2["LOGリストに, 学籍番号, 入室時刻, 退室時刻の行を追加"]
	UPD2-->UPD3["CURRENTリストの対応する入室時刻を削除"]
	UPD3-->NAME2["NAMEリストから学籍番号に対応する氏名を取得"]
	NAME2-->OUT2["jsonでname:名前, status:退室を返す"]
```

### コアタイム監視api
授業の開始時刻に実習室のPCから出す。
```mermaid
graph TD;
	POST["開始コマの番号を送信"]-->FETCH["ROSTERリストのコアタイム1,2を参照し, 該当学生番号を確認"]
	FETCH-->CHECK["該当者の学籍番号に対して, CURRENTリストの入室時刻が空であれば, 名前を記録"]
	CHECK-->LOG["ALERTリストに、学籍番号、日にち、時限を記録"]
	LOG-->ALERT["違反学籍番号を管理者のTELEGRAMに通告"]
```

### RESET用のapi
退室忘れの場合は入室を無効かします。
毎日0時に実習室のPCからリクエスト
```mermaid
graph TD;
	POST["RESET依頼"]-->UPD["CURRENTリスト入室時刻が空でない場合は、対応する学籍番号を記録し、入室時刻を空にする"]
	UPD-->ALERT["監視者のTelegramに違反学籍番号を通告"]
```

