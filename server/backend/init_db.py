from db.database import Base, engine
from models.models import Student, AttendanceLog, CurrentStatus, Alert

def init_db():
    # テーブルを作成
    Base.metadata.create_all(bind=engine)
    print("データベースを初期化しました。以下のテーブルが作成されました：")
    print("- Student（学生情報）")
    print("- AttendanceLog（出席記録）")
    print("- CurrentStatus（現在の入室状況）")
    print("- Alert（コアタイム違反等のアラート）")

if __name__ == "__main__":
    init_db() 