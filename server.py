import dotenv
from sqlmodel import create_engine, SQLModel
from models import User, Application, ApplicationAction, TimeLog, Notification

dotenv.load_dotenv()
import os

if __name__ == "__main__":
    db_url: str = os.getenv("DB_URL", "")
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
