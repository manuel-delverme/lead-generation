# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter
from sqlalchemy.orm import sessionmaker
from models import BusinessEntry, db_connect, create_businesses_table

class JsonWriterPipeline(object):
    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        fout = open('{}_data.jsonlines'.format(spider.name), 'w')
        self.files[spider] = fout
        self.exporter = JsonLinesItemExporter(fout)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        fout = self.files.pop(spider)
        fout.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class DatabasePipeline(object):
    def __init__(self):
        engine = db_connect()
        create_businesses_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
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
