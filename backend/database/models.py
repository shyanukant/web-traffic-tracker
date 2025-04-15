from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__= "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    websites = relationship("Website", back_populates="owner", cascade="all, delete-orphan")

class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="websites")

    visits = relationship("Visit", back_populates="website", cascade="all, delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"))
    ip = Column(String)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    location = Column(String)
    org = Column(String)
    browser = Column(String)
    browser_version = Column(String)
    os = Column(String)
    device = Column(String)
    url = Column(String)
    referrer = Column(String)
    screen = Column(String)
    time = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="visits")