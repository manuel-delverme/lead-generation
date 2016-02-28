# -*- coding: utf-8 -*-
import logging
import scrapy
import json
import scrapy.loader
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import SitemapSpider


class PagineSpider(SitemapSpider):
    sitemap_urls = [ "http://www.paginegialle.it/sitemap_schedeazienda_86.xml.gz", ]
    # sitemap_urls = ["http://localhost/sitemap_schedeazienda_86.xml.gz"]
    name = "sitemap_spider"
    handle_httpstatus_list = [200]

    def __init__(self, *a, **kw):
        super(PagineSpider, self).__init__(*a, **kw)

        self.default_cookies = {
            'pgz' : 'ODQ1ODg7VG9yaW5vO1RPOzkx',
            'D_SID':'93.50.188.12:FlUBu8vxe8ZJZDpu9HZjfXDrt9BiHIK/1PMtrtbkp2g;',
            '__rtgxg':'105DE627-354E-0001-3980-901019181DAD',
            '__rtgxh':'1455578137279$1455578132157$2',
            'kpi':'a98f9c65.52bd7386663c3',
            'sessionid':'8239027420012864366',
            'cp_acc':'1',
            's_cc':'true',
            's_fid':'7776CF06BE4467FF-0CF170173F114E17',
            's_lv':'1456255426652',
            's_nr':'1456255426654-Repeat',
            's_sq':'%5B%5BB%5D%5D',
            'D_PID':'C7A9E137-DBE9-34C8-9F83-E2C9DF26D3AC',
            'D_IID':'4256BE7B-BD96-36E6-ADCB-C5B66C6C4C48',
            'D_UID':'E68418E7-5E3D-3A81-884F-3EB9779ADDA1',
            'D_HID':'BTm//sv2uLSoVxQkw4Y63aDLfrhLEYHki6z6kM4t23U',
        }

    def parse(self, response):
        import ipdb;ipdb.set_trace()
        if response.url == "http://wwww.paginegialle.it":
            yield None
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
        #item['referrer'] = referrer
        item['microdata'] = microdata

        yield item
