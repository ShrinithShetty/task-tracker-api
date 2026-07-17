from sqlalchemy import Column, String, Integer
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False, index = True )
    email = Column(String, index = True,unique = True, nullable = False)
    fullname = Column(String, nullable = True)
    password = Column(String, nullable = False)

    

