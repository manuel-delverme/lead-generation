# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter
from sqlalchemy.orm import sessionmaker
from models import CompanyEntry, db_connect, create_businesses_table


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

    def parse(self, item):
        import ipdb; ipdb.set_trace()
        def find_source(item):
            if item['al_id'] != "" and item['al_link'] != "":
                return 1
            elif item['pg_id'] != "":
                return 0
            elif item['cb_code'] != "":
                # -> source
                return 3
            elif item['referrer'] != "":
                return 2
            else:
                return 4
        item['source'] = find_source(item)
        del item['referrer']
        del item['cb_code']
        del item['pg_id']
        del item['al_id']
        del item['crawled_url']

    def process_item(self, item, spider):
        session = self.Session()
        filtered_item = self.parse(item)
        business = CompanyEntry(**filtered_item)

        try:
            session.add(business)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
