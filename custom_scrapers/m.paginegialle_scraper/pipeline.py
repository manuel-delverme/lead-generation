# define DB structure
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

import datetime
import settings

DeclarativeBase = declarative_base()

def create_businesses_table(engine):
    DeclarativeBase.metadata.create_all(engine)


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


# init db connection

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


class DatabasePipeline(object):
    def __init__(self):
        engine = db_connect()
        create_businesses_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item):
        session = self.Session()
        business = BusinessEntry(**item)

        try:
            session.add(business)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
