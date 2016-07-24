# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
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

    def _find_source(self, item):
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

    def _add_meta_values(self, item):
        item['source'] = self._find_source(item)
        return item

    def _clean(self, item):

        # remove Nones
        for key, value in item.items():
            if not value:
                del item[key]

        # json can't handle sets
        for key, value in item.items():
            if isinstance(value, set):
                item[key] = json.dumps(list(value))


        # remove useless json serialization
        for key in ['homepage', 'formal_name', 'province', 'zip']:
            try:
                item[key] = json.loads(item[key])
            except (ValueError, KeyError):
                pass

        # some fields should be lists
        for key in ['emails', 'countries', 'cities', 'addresses']:
            try:
                item_obj = json.loads(item[key])
            except ValueError:
                print item['homepage'], ": could not decode", item[key], "as json"
            except KeyError:
                pass
            else:
                if isinstance(item_obj, list):
                    continue
                else:
                    item[key] = json.dumps([item_obj])

        # some fields are not needded anymore
        meta_fields = ['referrer', 'cb_code', 'pg_id', 'al_id', 'al_link', 'crawled_url', 'depth']
        for key in item.keys():
            if key in meta_fields:
                del item[key]
        return item

    def process_item(self, item, spider):
        if item['depth'] == 0:
            store_to_db = self.persist
        else:
            store_to_db = self.update_or_persist

        parsed_item = self.parse(item)
        import ipdb; ipdb.set_trace()
        self.store_to_disk(parsed_item)
        store_to_db(parsed_item)
        print "disabled persisting items!!!"

    def parse(self, item):
        crawled_url = item['crawled_url']
        item = self._add_meta_values(item)
        item = self._clean(item)
        print "added", crawled_url
        return item

    def store_to_disk(self, item):
        del item['body']

    def update_or_persist(self, item):
        try:
            self.update(item)
        except ValueError:
            self.persist(item)

    def update(self, item):
        session = self.Session()
        company = session.query(CompanyEntry).filter_by(homepage=item['homepage']).first()
        if not company:
            print "FAILED: parent not found", item['homepage']
            raise ValueError

        langs = set(json.loads(company.languages))
        langs.update(json.loads(item['languages']))
        company.languages = json.dumps(list(langs))
        session.add(company)
        session.commit()

    def persist(self, item):
        session = self.Session()
        company = CompanyEntry(**item)

        try:
            item_id = session.add(company)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return item_id
