import os
import requests
from typing import Optional

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> bool:
    """
    Telegramにメッセージを送信する

    Args:
        message (str): 送信するメッセージ

    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

def send_attendance_notification(student_id: str, student_name: str, status: str) -> bool:
    """
    出席状況の通知を送信する

    Args:
        student_id (str): 学籍番号
        student_name (str): 学生名
        status (str): 出席状況（"出席" or "欠席"）

    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    message = (
        f"<b>出席状況の更新</b>\n\n"
        f"学籍番号: {student_id}\n"
        f"氏名: {student_name}\n"
        f"状態: {status}"
    )
    return send_telegram_message(message)

def send_core_time_violation_notification(student_id: str, student_name: str, day: int, period: int) -> bool:
    """
    コアタイム違反の通知を送信する

    Args:
        student_id (str): 学籍番号
        student_name (str): 学生名
        day (int): 違反した日
        period (int): 違反した限目

    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    message = (
        f"<b>⚠️ コアタイム違反の通知</b>\n\n"
        f"学籍番号: {student_id}\n"
        f"氏名: {student_name}\n"
        f"違反日時: {day}日目 {period}限目"
    )
    return send_telegram_message(message) 