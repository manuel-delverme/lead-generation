# -*- coding: utf-8 -*-
import scrapy
#from items import CompaniesRA
import json


class ReportAziendeSpider(scrapy.Spider):
    name = "m.reportaziende.it"
    handle_httpstatus_list = [200]
    allowed_domains = ["reportaziende.it"]
    start_urls = [ "http://www.reportaziende.it/" ]
    f = open('provolone', 'w')

    def parse_companies(self, response):
        print "compania "+response.url

    def parse_w_links(self, response):
        for trgt in response.xpath("//ul[@class='carosello']/li/a/@href").extract():
            if trgt :
                url = response.urljoin(trgt)
                yield scrapy.Request(url, self.parse_companies)

    def parse(self, response):
        for trgt in response.xpath("///ul[@class='w_collegamenti']/li/a/@href").extract() :
            if trgt :
                url = response.urljoin(trgt)
                yield scrapy.Request(url, self.parse_w_links)




