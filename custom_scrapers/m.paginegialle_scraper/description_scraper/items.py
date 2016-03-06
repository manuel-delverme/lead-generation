# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Business(scrapy.Item):
    homepage = scrapy.Field()
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    dmoz_url = scrapy.Field()
    title = scrapy.Field()
    page_text = scrapy.Field()

    phones = scrapy.Field()
    addresses = scrapy.Field()
    cities = scrapy.Field()
    countries = scrapy.Field()
    emails = scrapy.Field()
    pg_id = scrapy.Field()
    name = scrapy.Field()
    province = scrapy.Field()
    zip = scrapy.Field()
