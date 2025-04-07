from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# Student schemas
class StudentBase(BaseModel):
    student_id: str
    name: str
    core_time_1_day: int = 0
    core_time_1_period: int = 0
    core_time_2_day: int = 0
    core_time_2_period: int = 0
    core_time_violations: int = 0

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    class Config:
        from_attributes = True

# AttendanceLog schemas
class AttendanceLogBase(BaseModel):
    student_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLog(AttendanceLogBase):
    id: int

    class Config:
        from_attributes = True

# CurrentStatus schemas
class CurrentStatusBase(BaseModel):
    student_id: str
    entry_time: datetime

class CurrentStatusCreate(CurrentStatusBase):
    pass

class CurrentStatus(CurrentStatusBase):
    class Config:
        from_attributes = True

# Alert schemas
class AlertBase(BaseModel):
    student_id: str
    alert_date: date
    alert_type: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int

    class Config:
        from_attributes = True 