# -*- coding: utf-8 -*-
import logging
import scrapy
import json
import glob
import scrapy.loader
from description_scraper.items import Company

class CrawlSpider(scrapy.Spider):
    name = "cb"
    
    allowed_domains = ["www.crunchbase.com"]
    start_urls = ( "https://www.crunchbase.com/funding-round/{}".format(funding_round) for funding_round in glob.glob("data/funding-rounds/*") )

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
        item['title'] = json.dumps(response.xpath("//title/text()").extract())
        item['homepage'] = response.url
        item['meta_description'] = json.dumps(response.xpath("//meta[@name='description']/@content").extract())
        item['meta_keywords'] = json.dumps(response.xpath("//meta[@name='keywords']/@content").extract())
        item['page_text'] = "" #  not used for now
        item['dmoz_url'] = response.meta['dmoz_url']
        yield item
