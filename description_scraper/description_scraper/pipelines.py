# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter

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
