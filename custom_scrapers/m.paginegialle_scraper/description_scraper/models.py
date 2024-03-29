# DB interface
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import datetime
import settings

DeclarativeBase = declarative_base()

def create_businesses_table(engine):
    DeclarativeBase.metadata.create_all(engine)

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

class BusinessEntry(DeclarativeBase):
    """Sqlalchemy entry model"""
    __tablename__ = "Businesses"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    homepage = Column('homepage', String)
    meta_description = Column('meta_description', String, nullable=True)
    meta_keywords = Column('meta_keywords', String, nullable=True)
    page_text = Column('page_text', String, nullable=True)
    dmoz_url = Column('referrer', String, nullable=True)
    crawl_time = Column('crawl_time', DateTime, default=datetime.datetime.utcnow)
    province = Column('province', String, nullable=True)
    zip = Column('zip', String, nullable=True)
    name = Column('common_name', String, nullable=True)
    pg_id = Column('pg_id', Integer, nullable=True)
    emails = Column('emails', String, nullable=True)
    countries = Column('countries', String, nullable=True)
    cities = Column('cities', String, nullable=True)
    addresses = Column('addresses', String, nullable=True)
    phones = Column('phones', String, nullable=True)
