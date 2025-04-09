#/api/projects/{project_number}/{researcher_number}/allocations

# {{{ import
from fastapi import FastAPI, HTTPException, Path, File, UploadFile, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import logging
import httpx
from xml.etree import ElementTree as ET
import base64
import json
import re
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List
from models.models import Student, AttendanceLog, CurrentStatus, Alert
from schemas.schemas import StudentCreate, Student as StudentSchema, AttendanceLogCreate, AttendanceLog as AttendanceLogSchema, CurrentStatusCreate, CurrentStatus as CurrentStatusSchema, AlertCreate, Alert as AlertSchema, AttendanceResponse
from db.database import get_db
# }}}

app = FastAPI(title="Attendance Manager API")

# CORSミドルウェアの設定
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # 本番環境では適切に制限してください
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# 静的ファイルの設定（APIエンドポイントの後にマウント）
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("../public/index.html", "r", encoding="utf-8") as f:
        return f.read()

#{{{ ロギングの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Start FastAPI")
#}}}

#{{{ # データベース接続
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "db/Attendance2025.db")

def get_db_connection():
	""" データベース接続を確立 """
	if not os.path.exists(DATABASE):
		logger.error(f"Nonexist: {DATABASE}")
		raise FileNotFoundError(f"Not exist: {DATABASE}")

	try:
		logger.info(f"Open Database: {DATABASE}")
		conn = sqlite3.connect(DATABASE)
		conn.row_factory = sqlite3.Row
		return conn
	except sqlite3.Error as e:
		logger.error(f"DB Error: {e}")
		raise HTTPException(status_code=500, detail="データベースに接続できませんでした")
#}}}

#{{{ 学生管理API
@app.post("/api/students/", response_model=StudentSchema)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
	db_student = Student(**student.dict())
	db.add(db_student)
	db.commit()
	db.refresh(db_student)
	return db_student

@app.get("/api/students/", response_model=List[StudentSchema])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	students = db.query(Student).offset(skip).limit(limit).all()
	return students

@app.get("/api/students/{student_id}", response_model=StudentSchema)
def read_student(student_id: str, db: Session = Depends(get_db)):
	student = db.query(Student).filter(Student.student_id == student_id).first()
	if student is None:
		raise HTTPException(status_code=404, detail="Student not found")
	return student
#}}}

#{{{ 入退室管理API
@app.post("/api/attendance/", response_model=AttendanceResponse)
def record_attendance(attendance: AttendanceLogCreate, db: Session = Depends(get_db)):
	# 学生が存在するか確認
	student = db.query(Student).filter(Student.student_id == attendance.student_id).first()
	if student is None:
		raise HTTPException(status_code=404, detail="Student not found")

	# 現在の入室状況を確認
	current_status = db.query(CurrentStatus).filter(
		CurrentStatus.student_id == attendance.student_id
	).first()

	if current_status is None:
		# 入室処理
		db_attendance = AttendanceLog(
			student_id=attendance.student_id,
			entry_time=attendance.time,
			exit_time=None  # 明示的にNoneを設定
		)
		db.add(db_attendance)
		
		# 現在の入室状況を更新
		current_status = CurrentStatus(
			student_id=attendance.student_id,
			entry_time=attendance.time
		)
		db.add(current_status)
		db.commit()
		return {"name": student.name, "status": "入室"}
	else:
		# 退室処理
		# 既存の入室記録を更新
		attendance_log = db.query(AttendanceLog).filter(
			AttendanceLog.student_id == attendance.student_id,
			AttendanceLog.exit_time.is_(None)  # exit_timeがNullのレコードを検索
		).order_by(AttendanceLog.entry_time.desc()).first()  # 最新の記録を取得
		
		if attendance_log:
			attendance_log.exit_time = attendance.time
		
		# 現在の入室状況を削除
		db.delete(current_status)
		db.commit()
		return {"name": student.name, "status": "退室"}

@app.get("/api/attendance/{student_id}", response_model=List[AttendanceLogSchema])
def read_student_attendance(
	student_id: str,
	days: int = 0,  # 日数パラメータを追加（デフォルトは0）
	db: Session = Depends(get_db)
):
	# 基本のクエリを作成
	query = db.query(AttendanceLog).filter(
		AttendanceLog.student_id == student_id
	)
	
	# 日数が0より大きい場合、指定された日数分のレコードを取得
	if days > 0:
		# 現在時刻から指定された日数分前の日時を計算
		cutoff_date = datetime.now() - timedelta(days=days)
		query = query.filter(AttendanceLog.entry_time >= cutoff_date)
	
	# レコードを取得（入室時刻の降順でソート）
	attendance_logs = query.order_by(AttendanceLog.entry_time.desc()).all()
	return attendance_logs

@app.get("/api/current-status/", response_model=List[CurrentStatusSchema])
def read_current_status(db: Session = Depends(get_db)):
	current_status = db.query(CurrentStatus).all()
	return current_status

@app.post("/api/attendance-now/{student_id}", response_model=AttendanceResponse)
def record_attendance_now(
	student_id: str,
	db: Session = Depends(get_db)
):
	"""
	現在時刻を使用して入退室を記録するエンドポイント
	"""
	# 現在時刻を取得
	current_time = datetime.now()
	
	# 学生の存在確認
	student = db.query(Student).filter(Student.student_id == student_id).first()
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	
	# 現在の入室状況を確認
	current_status = db.query(CurrentStatus).filter(
		CurrentStatus.student_id == student_id
	).first()
	
	if not current_status:
		# 入室処理
		current_status = CurrentStatus(
			student_id=student_id,
			entry_time=current_time
		)
		db.add(current_status)
		
		# 出席ログに記録
		attendance_log = AttendanceLog(
			student_id=student_id,
			entry_time=current_time,
			exit_time=None
		)
		db.add(attendance_log)
		
		db.commit()
		return AttendanceResponse(name=student.name, status="入室")
	else:
		# 退室処理
		# 出席ログを更新
		attendance_log = db.query(AttendanceLog).filter(
			AttendanceLog.student_id == student_id,
			AttendanceLog.exit_time == None
		).order_by(AttendanceLog.entry_time.desc()).first()
		
		if attendance_log:
			attendance_log.exit_time = current_time
		
		# 現在の入室状況を削除
		db.delete(current_status)
		db.commit()
		return AttendanceResponse(name=student.name, status="退室")
#}}}

#{{{ コアタイム管理API
@app.get("/api/core-time/check/{period}")
def check_core_time(period: int, db: Session = Depends(get_db)):
	current_time = datetime.now()
	current_day = current_time.weekday() + 1  # 1:月曜 2:火曜 ... 7:日曜
	
	# コアタイムの学生を取得
	students = db.query(Student).filter(
		((Student.core_time_1_day == current_day) & (Student.core_time_1_period == period)) |
		((Student.core_time_2_day == current_day) & (Student.core_time_2_period == period))
	).all()

	violations = []
	for student in students:
		# 入室状況を確認
		current_status = db.query(CurrentStatus).filter(
			CurrentStatus.student_id == student.student_id
		).first()
		
		if not current_status:
			# コアタイム違反
			violations.append(student.student_id)
			# 違反回数を更新
			student.core_time_violations += 1
			# アラートを記録
			alert = Alert(
				student_id=student.student_id,
				alert_date=current_time.date(),
				alert_type="core_time_violation"
			)
			db.add(alert)

	db.commit()
	return {"violations": violations}

@app.get("/api/core-time/violations", response_model=List[AlertSchema])
def read_core_time_violations(db: Session = Depends(get_db)):
	alerts = db.query(Alert).filter(
		Alert.alert_type == "core_time_violation"
	).all()
	return alerts
#}}}

# 静的ファイルの設定（最後にマウント）
app.mount("/js", StaticFiles(directory="../public/js"), name="js")
app.mount("/", StaticFiles(directory="../public", html=True), name="static")
