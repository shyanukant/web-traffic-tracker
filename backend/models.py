from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

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