# -*- coding: utf-8 -*-
import logging
import scrapy
import json
import scrapy.loader
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import SitemapSpider


class PagineSpider(SitemapSpider):
    sitemap_urls = ["http://www.paginegialle.it/sitemap_schedeazienda_86.xml.gz"]
    name = "sitemap_spider"
    handle_httpstatus_list = [200, 416]

    def __init__(self, *a, **kw):
        super(PagineSpider, self).__init__(*a, **kw)

        self.cookies = {
            'kpi': 'a354772a.52c858a6999a2',
            'iqhx': '5fcd55b6-a19a-4db5-9c72-00064c56336a',
            'sessionid': '3494561334330966717',
            'pgz': 'ODQ1ODg7VG9yaW5vO1RPOzkx',
            'listPositionUrlForCookie': '',
            'refererShiny': '',
            'priorityShiny': '',
            'argo': '',
            'D_SID': '93.49.205.65:OApKnFvt96qR1lfAuXnPLycIdjGfdhzvZMnouqDAjz0',
            'lst': '',
            'cookieClosed': 'ON',
            'idAdvertiser': '46616',
            'whereClosed': 'home',
            'cp_acc': '1',
            's_cc': 'true',
            'D_PID': '12B067DE-9F41-3610-85EC-D3FD7CFDD7F1',
            'D_IID': '6731853A-C865-3D36-9378-807F0AE9E6B5',
            'D_UID': 'E7D56644-BBD9-32D2-92CF-3EF86D72B3DE',
            'D_HID': 'lItTCJPowR66+sL60XNH/Xb35a9/oKcrlCCH+7s574g',
            '_ga': 'GA1.2.1126327956.1456326954',
            's_fid': '4B18C76ABC0CC80C-168E846D059AB94E',
            's_lv': '1456412467595',
            's_lv_s': 'Less%20than%201%20day',
            's_nr': '1456412467598-Repeat',
            'gpv_p24': 'PGIT%3AVhr%3AGuide%3ATorino%3AAlberg',
            's_sq': 'seatpgpgitprod%2Cseatpgglobalprod%3D%2526pid%253DPGIT%25253AVhr%25253AGuide%25253ATorino%25253AAlberg%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.paginegialle.it%25252Farthotelolympictorino%2526ot%253DA',
        }
        self.headers = {
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }

    def parse(self, response):
        import ipdb;ipdb.set_trace()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        extractor = MicrodataExtractor()
        items = extractor.extract(response.body_as_unicode(), response.url)['items']

        descriptions = response.xpath("//meta[@name='description']/@content").extract() + response.xpath("//meta[@property='og:description']/@content").extract()
        homepage_request = scrapy.Request(response.url,cookies=self.cookies, callback=self.parse_homepage, dont_filter=True)
        # TODO remove don't filter = True
        homepage_request.meta['dt_pg_description'] = descriptions
        homepage_request.meta['dt_pg_keywords'] = response.xpath("//meta[@name='keywords']/@content").extract()
        homepage_request.meta['dt_pg_title'] = response.xpath("//meta[@property='og:title']/@content").extract()
        homepage_request.meta['dt_microdata'] = items
        homepage_request.meta['dt_referrer'] =  response.url
        yield homepage_request

    def parse_homepage(self, response):
        item = Business()

        title = response.meta['dt_pg_title']
        meta_description = response.meta['dt_pg_description']
        meta_keywords = response.meta['dt_pg_keywords']
        microdata = response.meta['dt_microdata']
        referrer = response.meta['dt_referrer']

        title += response.xpath("//title/text()").extract()
        meta_keywords += response.xpath("//meta[@name='keywords']/@content").extract()
        meta_description += response.xpath("//meta[@name='description']/@content").extract()

        item['title'] = json.dumps(title)
        item['homepage'] = response.url
        item['meta_description'] = json.dumps(meta_description)
        item['meta_keywords'] = json.dumps(meta_keywords)
        item['page_text'] = "" #  not used for now
        item['referrer'] = referrer
        item['microdata'] = microdata

        yield item
