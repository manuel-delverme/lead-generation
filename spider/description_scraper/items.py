# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Company(scrapy.Item):
    formal_name = scrapy.Field()
    homepage = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()

    # address
    province = scrapy.Field()
    zip = scrapy.Field()

    languages = scrapy.Field()

    # 0,1,2,3
    source = scrapy.Field()
    emails = scrapy.Field()
    countries = scrapy.Field()
    cities = scrapy.Field()
    addresses = scrapy.Field()
    phones = scrapy.Field()
    countries = scrapy.Field()

    peer_companies = scrapy.Field()
    revenue = scrapy.Field()
    employees_min = scrapy.Field()
    employees_max = scrapy.Field()
    funding = scrapy.Field()

    # source
    pg_id = scrapy.Field()
    al_id = scrapy.Field()
    al_link = scrapy.Field()
    cb_id = scrapy.Field()
    dmoz_url = scrapy.Field()
    crawled_url = scrapy.Field()
    depth = scrapy.Field()


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
