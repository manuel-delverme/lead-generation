# -*- coding: utf-8 -*-
import logging
import scrapy
import json
import scrapy.loader
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import SitemapSpider


class PagineSpider(SitemapSpider):
    sitemap_urls = ['http://www.paginegialle.it/sitemap.xml']
    name = "sitemap_spider"

    def parse(self, response):
        extractor = MicrodataExtractor()
        items = extractor.extract(response.body_as_unicode(), response.url)['items']

        descriptions = response.xpath("//meta[@name='description']/@content").extract() + response.xpath("//meta[@property='og:description']/@content").extract()
        request = scrapy.Request(url, callback=self.parse_homepage)
        request.meta['pg_description'] = descriptions
        request.meta['pg_keywords'] = response.xpath("//meta[@name='keywords']/@content").extract()
        request.meta['pg_title'] = response.xpath("//meta[@property='og:title']/@content").extract()
        request.meta['microdata'] = items
        request.meta['referrer'] =  response.url
        yield request

    def parse_homepage(self, response):
        item = Business()

        title = request.meta['pg_title']
        meta_description = request.meta['pg_description']
        meta_keywords = request.meta['pg_keywords']
        microdata = request.meta['microdata']
        referrer = request.meta['referrer']

        title += response.xpath("//title/text()").extract()
        meta_keywords += response.xpath("//meta[@name='keywords']/@content").extract()
        meta_description += response.xpath("//meta[@name='description']/@content").extract()

        item['title'] = json.dumps(title)
        item['homepage'] = response.url
        item['meta_description'] = json.dumps(meta_description)
        item['meta_keywords'] = json.dumps(meta_keywords)
        item['page_text'] = "" #  not used for now
        item['referrer'] = referrer
        item['microdata'] = referrer
        yield item
