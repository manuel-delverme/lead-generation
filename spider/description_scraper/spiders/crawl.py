# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy.loader
import psycopg2
import psycopg2.extras
from description_scraper.items import Business


class CrawlSpider(scrapy.Spider):
    name = "website_crawler"

    def __init__(self, **kwargs):
        super(CrawlSpider, self).__init__(**kwargs)
        connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", "write_only")
        self._conn = psycopg2.connect(connect_string)

    def start_requests(self):
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # cursor.execute('select * from "Businesses" where homepage != $$""$$ limit 100')  # crawl_time is NULL')
            cursor.execute('select DISTINCT homepage from "Businesses" where homepage != $$""$$ limit 100')  # crawl_time is NULL')
            for db_entry in cursor:
                homepage = db_entry['homepage']
                try:
                    homepage = json.loads(db_entry['homepage'])
                except ValueError:

                    if homepage[0] == '"' and homepage[-1] == '"':
                        homepage = homepage[1:-1]
                    elif homepage[0] == '{' and homepage[-1] == '}':
                        homepage = homepage[1:-1]

                    if "," in homepage:
                        entry_urls = homepage.split(",")
                    else:
                        entry_urls = [homepage]
                else:
                    if type(homepage) in (unicode, str):
                        entry_urls = [homepage]
                    elif type(homepage) == list:
                        pass
                    else:
                        import ipdb
                        ipdb.set_trace()
                if entry_urls is None:
                    ipdb.set_trace()
                for homepage in entry_urls:
                    req = scrapy.Request(homepage, callback=self.parse_homepage, meta={'old_db_entry': db_entry})
                    yield req

    def parse_homepage(self, response):
        # push back all the urls
        import ipdb
        ipdb.set_trace()
        # find if export // languages
        # langues = languages_in_page
        # fom angelList only
        for url in response.css("a").filter(response.url.baseurl):
            if url.baseurl == response.baseurl:
                yield scrapy.Request(url, callback=self.parse)

        item = Business()
        item['title'] = self.get_name(response)
        item['homepage'] = response.url
        item['meta_description'] = json.dumps(response.xpath("//meta[@name='description']/@content").extract())
        item['meta_keywords'] = json.dumps(response.xpath("//meta[@name='keywords']/@content").extract())
        item['page_text'] = ""  # not used for now
        item['dmoz_url'] = response.meta['dmoz_url']
        yield item

    def get_name(self, response):
        try:
            response.xpath("footer -> title").extract()
            response.xpath("//title/text()").extract()
        except:
            response.xpath("fallback to pg").extract()
