# -*- coding: utf-8 -*-
import scrapy
# import json
import scrapy.loader
import psycopg2
import psycopg2.extras
import langdetect
import description_scraper.isocodes
import scrapy.utils.url
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
# from description_scraper.items import Company


class CrawlSpider(scrapy.Spider):
    name = "website_crawler"

    def __init__(self, **kwargs):
        super(CrawlSpider, self).__init__(**kwargs)
        connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", "write_only")
        self._conn = psycopg2.connect(connect_string)

    def clean_urls(self, string):
        
    def start_requests(self):
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # cursor.execute('select * from "Businesses" where homepage != $$""$$ limit 100')  # crawl_time is NULL')
            cursor.execute('select DISTINCT homepage from "Businesses" where homepage != $$""$$ and pg_id != $$""$$ OFFSET floor(random()*12345) LIMIT 1;')  # crawl_time is NULL')
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
                    import ipdb
                    ipdb.set_trace()
                for homepage in entry_urls:
                    netloc = scrapy.utils.url.parse_url(homepage).netloc
                    if not netloc:
                        homepage = "http://" + homepage
                    req = scrapy.Request(homepage, callback=self.parse_homepage, meta={'old_db_entry': db_entry})
                    yield req
        """

    def parse_homepage(self, response):
        # push back all the urls
        # find if export // languages
        # langues = languages_in_page
        # fom angelList only

        in_links_extractor = LinkExtractor(allow=(response.url), unique=True)
        for link in in_links_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_homepage)

        item['languages'] = self.get_languages(response)
        yield None
        """
        item = Company()
        item['title'] = self.get_name(response)
        item['languages'] = self.get_languages(response, out_links_extractor)
        item['peer_companies'] = self.get_languages(response, out_links_extractor)
        item['homepage'] = response.url
        item['meta_description'] = json.dumps(response.xpath("//meta[@name='description']/@content").extract())
        item['meta_keywords'] = json.dumps(response.xpath("//meta[@name='keywords']/@content").extract())
        item['page_text'] = ""  # not used for now
        # item['dmoz_url'] = response.meta['dmoz_url']
        yield item
        """

    def all_tld_domains(self, response):
        out_links_extractor = LinkExtractor(deny=(response.url), unique=True)
        tlds = []
        not_tlds = []
        netloc = scrapy.utils.url.parse_url(response.url).netloc
        basedomain = netloc[:netloc.rindex(".")]

        for link in out_links_extractor.extract_links(response):
            base_url = link.url[:link.url.rindex(".")]
            if base_url == basedomain:
                tlds.append(netloc.split(".")[-1])
            else:
                not_tlds.append(netloc)
        return tlds, set(not_tlds)

    def get_languages(self, response):
        # print self.all_tld_domains(response, out_links_extractor)
        tlds, _ = self.all_tld_domains(response)
        query_string = scrapy.utils.url.parse_url(response.url).query
        query = scrapy.utils.url.parse_qsl(query_string)
        for key, val in query:
            if val in description_scraper.isocodes.languages:
                print "---------------->", val

        # "?lang=en"
        # TODO this should be on all the text
        soup = BeautifulSoup(response.body)
        languages = langdetect.detect_langs(soup.getText())

        return languages

    def get_name(self, response):
        try:
            response.xpath("footer -> title").extract()
            response.xpath("//title/text()").extract()
        except:
            response.xpath("fallback to pg").extract()

    def related_companies(self):
        # www.site.*
        # check DNS
        raise NotImplementedError
