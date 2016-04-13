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


class CompanyEntry(DeclarativeBase):
    """Sqlalchemy entry model"""
    __tablename__ = "Company"

    id = Column(Integer, primary_key=True)
    formal_name = Column('formal_name', String)
    homepage = Column('homepage', String)
    description = Column('description', String, nullable=True)
    keywords = Column('keywords', String, nullable=True)
    # page_text = Column('page_text', String, nullable=True)
    # dmoz_url = Column('referrer', String, nullable=True)
    crawl_time = Column('crawl_time', DateTime, default=datetime.datetime.utcnow)
    province = Column('province', String, nullable=True)
    zip = Column('zip', String, nullable=True)
    name = Column('common_name', String, nullable=True)
    languages = Column('languages', String, nullable=True)
    # pg = 0, al = 1, dmoz = 2, cb = 3
    source = Column('source', Integer, nullable=True)
    emails = Column('emails', String, nullable=True)
    countries = Column('countries', String, nullable=True)
    cities = Column('cities', String, nullable=True)
    addresses = Column('addresses', String, nullable=True)
    phones = Column('phones', String, nullable=True)
    employees_max = Column('employees_max', Integer, nullable=True)
    employees_min = Column('employees_min', Integer, nullable=True)
    funding = Column('funding', Integer, nullable=True)
    funding_currency = Column('funding_currency', String, nullable=True)
    peer_companies = Column('peer_companies', String, nullable=True)
