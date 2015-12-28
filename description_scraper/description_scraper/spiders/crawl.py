# -*- coding: utf-8 -*-
import logging
import scrapy
import scrapy.loader
from description_scraper.items import Business


class CrawlSpider(scrapy.Spider):
    name = "crawl"
    # allowed_domains = ["www.dmoz.org"]
    start_urls = (
        'http://www.dmoz.org/World/Italiano/Affari/',
    )

    def parse(self, response):

        hrefs = response.css("ul.directory-url > li > a::attr('href')")
        for href in hrefs:
            url = response.urljoin(href.extract())

            request = scrapy.Request(url, callback=self.parse_homepage)
            request.meta['dmoz_url'] =  response.url
            yield request

        sub_directories = response.css("ul.directory.dir-col > li > a::attr('href')")
        for href in sub_directories:
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

    def parse_homepage(self, response):
        item = Business()
        item['homepage'] = response.url
        item['dmoz_url'] = response.meta['dmoz_url']
        item['metadata'] = response.xpath("//meta[@name='description']/@content").extract()
        yield item
