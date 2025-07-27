from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0) # 0 for client, 1 for admin
    
    streams = relationship("Stream", secondary="user_streams")

class FlussonicServer(Base):
    __tablename__ = "flussonic_servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)

class Stream(Base):
    __tablename__ = "streams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    server_id = Column(Integer, ForeignKey("flussonic_servers.id"))
    
    server = relationship("FlussonicServer")
    users = relationship("User", secondary="user_streams")

class UserStream(Base):
    __tablename__ = "user_streams"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), primary_key=True)

class TrafficUsage(Base):
    __tablename__ = "traffic_usage"
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    usage_gb = Column(Float, nullable=False)

    stream = relationship("Stream")
