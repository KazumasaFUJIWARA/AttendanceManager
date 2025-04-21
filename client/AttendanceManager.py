#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AttendanceManager.py - NFC読み取りクライアント（APIサーバー連携版）
#

# ライブラリのインポート
import tkinter as tk
from tkinter import ttk
from tkinter import font
import nfc
from nfc.tag import Tag
from nfc.tag.tt3 import BlockCode, ServiceCode, Type3Tag
from nfc.tag.tt3_sony import FelicaStandard
import time
import threading
import json
import requests
import sys
import os
from typing import cast
from datetime import datetime
import queue

# 設定
URL = os.environ.get("ATTEND_SERVER")
API_BASE_URL = "http://" + URL + "/api"  # APIサーバーのベースURL
WINDOW_TITLE = "出席管理システム"
BACKGROUND_COLOR = "black"
TEXT_COLOR = "green"
ERROR_COLOR = "red"  # エラー表示用の色を追加
FONT_FAMILY = "Arial"  # Debianでも利用可能なフォントに変更
FONT_SIZE = 22
TITLE_FONT_SIZE = 28
SYSTEM_CODE = 0x809E  # FeliCaのシステムコード

# グローバル変数
close_order = False

# メインウィンドウの設定
class AttendanceManagerApp:
	def __init__(self, root):
		self.root = root
		self.setup_ui()
		self.message_queue = queue.Queue()  # メッセージキューを追加
		
		# メッセージ処理の定期実行を開始
		self.process_messages()
		
		# NFCリーダースレッドの開始
		self.nfc_thread = threading.Thread(target=self.nfc_read_loop)
		self.nfc_thread.daemon = True
		self.nfc_thread.start()

	def setup_ui(self):
		# ウィンドウの基本設定
		self.root.title(WINDOW_TITLE)
		self.root.attributes('-fullscreen', True)
		self.root.configure(bg=BACKGROUND_COLOR)
		self.root['padx'] = 100
		self.root['pady'] = 100

		# フォントの設定
		default_font = font.nametofont("TkDefaultFont")
		try:
			default_font.configure(family=FONT_FAMILY, size=FONT_SIZE)
		except tk.TclError:
			default_font.configure(family="Arial", size=FONT_SIZE)  # フォールバック
		title_font = (FONT_FAMILY, TITLE_FONT_SIZE)
		
		# スタイルの設定
		style = ttk.Style()
		style.configure("TButton", padding=15, foreground=TEXT_COLOR, background=BACKGROUND_COLOR, font=(FONT_FAMILY, FONT_SIZE))
		style.configure("Small.TButton", padding=5, foreground=TEXT_COLOR, background=BACKGROUND_COLOR, font=(FONT_FAMILY, FONT_SIZE-8))
		style.configure("Error.TLabel", foreground=ERROR_COLOR, background=BACKGROUND_COLOR, font=(FONT_FAMILY, FONT_SIZE))

		# メッセージ表示用の変数
		self.system_message1 = tk.StringVar()
		self.system_message2 = tk.StringVar()
		self.response_message = tk.StringVar()
		
		self.system_message1.set("システム: カードをリーダーにかざしてください")
		self.system_message2.set("システム: 読み取り待機中...")
		self.response_message.set("")

		# UI要素の配置
		title = tk.Label(self.root, text="出席管理システム", font=title_font, foreground=TEXT_COLOR, bg=BACKGROUND_COLOR)
		title.grid(column=0, row=0, columnspan=3, pady=(0, 30))
		
		# システムメッセージの表示
		system_output1 = tk.Label(self.root, textvariable=self.system_message1, foreground=TEXT_COLOR, bg=BACKGROUND_COLOR, pady=10)
		system_output2 = tk.Label(self.root, textvariable=self.system_message2, foreground=TEXT_COLOR, bg=BACKGROUND_COLOR, pady=10)
		system_output1.grid(row=1, column=0, columnspan=3, sticky=tk.W)
		system_output2.grid(row=2, column=0, columnspan=3, sticky=tk.W)
		
		# APIレスポンス表示エリア
		response_area = tk.Label(self.root, textvariable=self.response_message, foreground=TEXT_COLOR, bg=BACKGROUND_COLOR, pady=20, justify=tk.LEFT)
		response_area.grid(row=3, column=0, columnspan=3, sticky=tk.W)
		
		# 列の設定
		self.root.columnconfigure(0, weight=2)
		self.root.columnconfigure(1, weight=1)
		self.root.columnconfigure(2, weight=1)

	def process_messages(self):
		"""メッセージキューからメッセージを処理"""
		try:
			while True:
				message = self.message_queue.get_nowait()
				if message.get('type') == 'system1':
					self.system_message1.set(message['text'])
				elif message.get('type') == 'system2':
					self.system_message2.set(message['text'])
				elif message.get('type') == 'response':
					self.response_message.set(message['text'])
				elif message.get('type') == 'error':
					# エラーメッセージは赤色で表示
					self.system_message1.set(message['text'])
					self.system_message2.set("")
					self.response_message.set("")
		except queue.Empty:
			pass
		finally:
			# 100ミリ秒後に再度チェック
			self.root.after(100, self.process_messages)

	def update_ui(self, message_type: str, text: str):
		"""スレッドセーフなUI更新"""
		self.message_queue.put({'type': message_type, 'text': text})

	def window_close(self):
		"""アプリケーションの終了処理"""
		global close_order
		close_order = True
		self.root.after(1000, self.root.destroy)  # 1秒後にウィンドウを閉じる

	def read_data_block(self, tag: Type3Tag, service_code_number: int, block_code_number: int) -> bytearray:
		"""FeliCaカードからデータブロックを読み取る"""
		service_code = ServiceCode(service_code_number, 0x0B)
		block_code = BlockCode(block_code_number)
		try:
			read_bytearray = cast(bytearray, tag.read_without_encryption([service_code], [block_code]))
			return read_bytearray
		except Exception as e:
			self.system_message1.set(f"システム: データ読み取りエラー")
			self.system_message2.set(f"エラー内容: {str(e)}")
			return bytearray()

	def get_student_id(self, tag: Type3Tag) -> str:
		"""学生IDの読み取り（テストカード用）"""
		try:
			student_id_bytearray = self.read_data_block(tag, 106, 0)
			return student_id_bytearray.decode().strip()
		except:
			# 読み取りに失敗した場合はIDmを代わりに使用
			return tag.identifier.hex()

	def on_connect(self, tag: Tag) -> bool:
		"""NFCカード接続時の処理"""
		self.system_message1.set("システム: カードを検出しました")
		self.system_message2.set("カード情報を読み取り中...")
		
		try:
			# FeliCaカードの場合の処理
			if isinstance(tag, FelicaStandard) and SYSTEM_CODE in tag.request_system_code():  # カードがFeliCaでかつシステムコードが存在する場合
				tag.idm, tag.pmm, *_ = tag.polling(0xFE00)
				student_id = self.get_student_id(tag)
				# 不要な文字を削除して小文字に変更
				student_id = student_id[2:-2].lower().strip('\x00')
				self.handle_card_read(student_id)
		except Exception as e:
			self.system_message1.set(f"システム: カード読み取りエラー")
			self.system_message2.set(f"エラー内容: {str(e)}")
			
		return True  # カードが離れるまで待機

	def on_release(self, tag: Tag) -> None:
		"""カードがリーダーから離れた時の処理"""
		self.system_message1.set("システム: カードをリーダーにかざしてください")
		self.system_message2.set("システム: 読み取り待機中...")

	def nfc_read_loop(self):
		"""NFCカード読み取りのメインループ"""
		global close_order
		
		while not close_order:
			try:
				# NFCリーダーの初期化（with構文で自動クローズ）
				with nfc.ContactlessFrontend('usb') as clf:
					# カード接続待機
					self.update_ui('system1', "システム: カードをリーダーにかざしてください")
					self.update_ui('system2', "システム: 読み取り待機中...")
					
					# カード読み取り
					clf.connect(rdwr={
						"on-connect": self.on_connect, 
						"on-release": self.on_release
					}, terminate=lambda: close_order)
				
			except Exception as e:
				error_message = f"NFCリーダーのエラー: {str(e)}"
				self.update_ui('system1', "システム: NFCリーダーのエラーが発生しました")
				self.update_ui('system2', f"エラー内容: {str(e)}")
				self.log_to_file(error_message)
				time.sleep(3)
				
			time.sleep(1)  # ループの間隔を設定

	def log_to_file(self, message: str):
		"""ログをファイルに記録"""
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log_message = f"{timestamp} - {message}\n"
		
		try:
			with open("attend.log", "a", encoding="utf-8") as f:
				f.write(log_message)
		except Exception as e:
			print(f"ログファイル書き込みエラー: {e}")

	def handle_card_read(self, card_id):
		"""カードが読み取られた時の処理"""
		self.system_message1.set("システム: カードを読み取りました")
		self.system_message2.set(f"カードID: {card_id}")
		self.log_to_file(f"カード読み取り: {card_id}")
		
		try:
			# APIに入退室データを送信
			self.send_attendance_data(card_id)
		except Exception as e:
			error_message = f"カード読み取りエラー: {str(e)}"
			self.system_message1.set("システム: APIとの通信中にエラーが発生しました")
			self.system_message2.set(f"エラー内容: {str(e)}")
			self.response_message.set("")
			self.log_to_file(error_message)
		
	def send_attendance_data(self, card_id):
		"""APIサーバーに入退室データを送信"""
		url = f"{API_BASE_URL}/attendance-now/{card_id}"
		headers = {
		    "accept": "application/json"
		}
		
		self.system_message1.set("システム: サーバーと通信中...")
		self.system_message2.set("しばらくお待ちください...")
		
		try:
			response = requests.post(url, headers=headers)
			
			if response.status_code == 200:
				# 成功時の処理
				data = response.json()
				name = data.get("name", "不明")
				status = data.get("status", "不明")
				
				# 日本語で状態を表示
				status_text = "入室" if status == "入室" else "退室"
				
				self.system_message1.set(f"システム: {name} さんが{status_text}しました")
				self.system_message2.set(f"現在の状態: {status_text}")
				
				# レスポンスの詳細を表示
				self.response_message.set(f"名前: {name}\n状態: {status_text}\n時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
				
				# ログに記録
				self.log_to_file(f"入退室記録: {name} - {status_text}")
				
			else:
				# エラー時の処理
				error_message = f"APIリクエスト失敗: {response.status_code} - {response.text}"
				self.system_message1.set("システム: APIリクエストが失敗しました")
				self.system_message2.set(f"ステータスコード: {response.status_code}")
				self.response_message.set(f"エラー内容: {response.text}")
				self.log_to_file(error_message)
				
		except requests.exceptions.RequestException as e:
			# 通信エラー時の処理
			error_message = f"サーバー通信エラー: {str(e)}"
			self.system_message1.set("システム: サーバーとの通信に失敗しました")
			self.system_message2.set("ネットワーク接続を確認してください")
			self.response_message.set(f"エラー内容: {str(e)}")
			self.log_to_file(error_message)

	def get_student_info(self, student_id):
		"""学生IDから学生情報を取得"""
		url = f"{API_BASE_URL}/students/{student_id}"
		
		try:
			response = requests.get(url)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.RequestException as e:
			print(f"学生情報取得エラー: {e}")
			raise

	def get_attendance_history(self, student_id, days=7):
		"""指定された学生の出席履歴を取得"""
		url = f"{API_BASE_URL}/attendance/{student_id}?days={days}"
		
		try:
			response = requests.get(url)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.RequestException as e:
			print(f"出席履歴取得エラー: {e}")
			raise

# メイン処理
if __name__ == "__main__":
	# アプリケーションの開始
	root = tk.Tk()
	app = AttendanceManagerApp(root)
	root.mainloop()
