from sqlalchemy import Integer, Column, String, Boolean
from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    description = Column(String, nullable = False)
    completed = Column(Boolean, default = False)


