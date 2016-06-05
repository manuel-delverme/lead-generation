# -*- coding: utf-8 -*-
import scrapy
#from items import CompaniesRA
import os
import urllib

class ReportAziendeSpider(scrapy.Spider):

    name = "m.reportaziende.it"
    handle_httpstatus_list = [200]
    allowed_domains = ["reportaziende.it"]
    start_urls = [ "http://www.reportaziende.it/" ]

    def parse_confronto(self, response):
        f = open(urllib.pathname2url(response.url[7:]),"w")
        f.write(response.body)

    def parse_dati(self, response):
    	f = open(urllib.pathname2url(response.url[7:]),"w")
        f.write(response.body)

    def parse_companies(self, response):
        ys = [2011,2013]
        oldUrl = response.url

        for y in ys :
        	url = oldUrl+"?anno2="+str(y)+"&anno1="+str(y+1)+"#confronto"
        	yield scrapy.Request(url, self.parse_confronto)

       	ys = [2011,2012,2013,2014]
       	
       	for y in ys:
       		url=oldUrl+"?anno3="+str(y)+"#dati"
       		yield scrapy.Request(url, self.parse_dati)

    def parse_w_links(self, response):
        for trgt in response.xpath("//ul[@class='carosello']/li/a/@href").extract():
            if trgt :
                url = response.urljoin(trgt)
                yield scrapy.Request(url, self.parse_companies)

    def parse(self, response):
        if not os.path.isdir("./www.reportaziende.it/"):
            os.mkdir("./www.reportaziende.it/")
        for trgt in response.xpath("///ul[@class='w_collegamenti']/li/a/@href").extract() :
            if trgt :
                url = response.urljoin(trgt)
                yield scrapy.Request(url, self.parse_w_links)




