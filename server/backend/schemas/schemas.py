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
class AttendanceLogCreate(BaseModel):
    student_id: str
    time: datetime  # entry_timeからtimeに変更

class AttendanceLog(BaseModel):
    id: Optional[int] = None
    student_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class AttendanceResponse(BaseModel):
    name: str
    status: str

# CurrentStatus schemas
class CurrentStatusBase(BaseModel):
    student_id: str
    entry_time: Optional[datetime] = None

class CurrentStatusCreate(CurrentStatusBase):
    pass

class CurrentStatus(CurrentStatusBase):
    class Config:
        from_attributes = True

# Alert schemas
class AlertBase(BaseModel):
    student_id: str
    alert_date: date
    alert_period: int

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int

    class Config:
        orm_mode = True

# CoreTime schemas
class CoreTimeUpdate(BaseModel):
    core_time_1_day: int
    core_time_1_period: int
    core_time_2_day: int
    core_time_2_period: int

    class Config:
        json_schema_extra = {
            "example": {
                "core_time_1_day": 1,
                "core_time_1_period": 1,
                "core_time_2_day": 3,
                "core_time_2_period": 2
            }
        } 