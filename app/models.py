from sqlalchemy import Integer, String, Column, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    role_name = Column(String, nullable=False)

    
class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, nullable=False, primary_key=True)
    task_name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), default=None)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    creator = relationship("User", foreign_keys=[creator_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])

class Tokens(Base):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, index=True, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    tk = relationship("User")