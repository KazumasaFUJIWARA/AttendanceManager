from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    core_time_1_day = Column(Integer, default=0)
    core_time_1_period = Column(Integer, default=0)
    core_time_2_day = Column(Integer, default=0)
    core_time_2_period = Column(Integer, default=0)
    core_time_violations = Column(Integer, default=0)

    # リレーションシップ
    attendance_logs = relationship("AttendanceLog", back_populates="student")
    current_status = relationship("CurrentStatus", back_populates="student", uselist=False)
    alerts = relationship("Alert", back_populates="student")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.student_id"))
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)

    # リレーションシップ
    student = relationship("Student", back_populates="attendance_logs")

class CurrentStatus(Base):
    __tablename__ = "current_status"

    student_id = Column(String, ForeignKey("students.student_id"), primary_key=True)
    entry_time = Column(DateTime)

    # リレーションシップ
    student = relationship("Student", back_populates="current_status")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.student_id"))
    alert_date = Column(Date, nullable=False)
    alert_period = Column(Integer, nullable=False)

    # リレーションシップ
    student = relationship("Student", back_populates="alerts") 