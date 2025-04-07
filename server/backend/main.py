#/api/projects/{project_number}/{researcher_number}/allocations

# {{{ import
from fastapi import FastAPI, HTTPException, Path, File, UploadFile, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
from datetime import datetime, date
from typing import List
from models.models import Student, AttendanceLog, CurrentStatus, Alert
from schemas.schemas import StudentCreate, Student, AttendanceLogCreate, AttendanceLog, CurrentStatusCreate, CurrentStatus, AlertCreate, Alert
from db.database import get_db
# }}}

app = FastAPI(title="Attendance Manager API")

#{{{ ロギングの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Start FastAPI")
#}}}

# 静的ファイルを "/static" にマウント
app.mount("/static", StaticFiles(directory="/app/public"), name="static")

# ルートパス "/" で index.html を返す
@app.get("/")
async def read_index():
	return FileResponse("/app/public/index.html")

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
@app.post("/api/students/", response_model=Student)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
	db_student = Student(**student.dict())
	db.add(db_student)
	db.commit()
	db.refresh(db_student)
	return db_student

@app.get("/api/students/", response_model=List[Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	students = db.query(Student).offset(skip).limit(limit).all()
	return students

@app.get("/api/students/{student_id}", response_model=Student)
def read_student(student_id: str, db: Session = Depends(get_db)):
	student = db.query(Student).filter(Student.student_id == student_id).first()
	if student is None:
		raise HTTPException(status_code=404, detail="Student not found")
	return student
#}}}

#{{{ 入退室管理API
@app.post("/api/attendance/", response_model=AttendanceLog)
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
		db_attendance = AttendanceLog(**attendance.dict())
		db.add(db_attendance)
		
		# 現在の入室状況を更新
		current_status = CurrentStatus(
			student_id=attendance.student_id,
			entry_time=attendance.entry_time
		)
		db.add(current_status)
	else:
		# 退室処理
		# 既存の入室記録を更新
		attendance_log = db.query(AttendanceLog).filter(
			AttendanceLog.student_id == attendance.student_id,
			AttendanceLog.exit_time.is_(None)
		).first()
		if attendance_log:
			attendance_log.exit_time = attendance.entry_time
		
		# 現在の入室状況を削除
		db.delete(current_status)

	db.commit()
	return attendance_log

@app.get("/api/attendance/{student_id}", response_model=List[AttendanceLog])
def read_student_attendance(student_id: str, db: Session = Depends(get_db)):
	attendance_logs = db.query(AttendanceLog).filter(
		AttendanceLog.student_id == student_id
	).all()
	return attendance_logs

@app.get("/api/current-status/", response_model=List[CurrentStatus])
def read_current_status(db: Session = Depends(get_db)):
	current_status = db.query(CurrentStatus).all()
	return current_status
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

@app.get("/api/core-time/violations", response_model=List[Alert])
def read_core_time_violations(db: Session = Depends(get_db)):
	alerts = db.query(Alert).filter(
		Alert.alert_type == "core_time_violation"
	).all()
	return alerts
#}}}
