# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MediaArticle(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    summary = scrapy.Field()
    authors = scrapy.Field()
    domain = scrapy.Field()
    date = scrapy.Field()
    pass
