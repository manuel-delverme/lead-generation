# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy.loader
import psycopg2
import psycopg2.extras
import langdetect
import description_scraper.isocodes
import scrapy.utils.url
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from description_scraper.items import Company


class CrawlSpider(scrapy.Spider):
    name = "website_crawler"

    def __init__(self, **kwargs):
        super(CrawlSpider, self).__init__(**kwargs)
        connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", "write_only")
        self._conn = psycopg2.connect(connect_string)

    def clean_urls(self, dirty_urls):
        def remove_serialization(url):
            if url[0] == '"' and url[-1] == '"':
                url = url[1:-1]

            if url[0] == '{' and url[-1] == '}':
                url = url[1:-1]
            return url

        try:
            entry_urls = json.loads(dirty_urls)
        except ValueError:
            entry_urls = remove_serialization(dirty_urls)

            if "," in entry_urls:
                entry_urls = dirty_urls.split(",")
            else:
                entry_urls = [dirty_urls]
        else:
            if type(entry_urls) in (unicode, str):
                entry_urls = [entry_urls]
            elif type(entry_urls) == list:
                pass
            else:
                import ipdb
                ipdb.set_trace()

        if entry_urls is None:
            import ipdb
            ipdb.set_trace()

        entry_urls = [remove_serialization(url) for url in entry_urls]
        return entry_urls

    def start_requests(self):
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # cursor.execute('select * from "Businesses" where homepage != $$""$$ limit 100')  # crawl_time is NULL')
            cursor.execute('select DISTINCT homepage from "Businesses" where homepage != $$""$$ and pg_id != $$""$$ OFFSET floor(random()*12345) LIMIT 1;')  # crawl_time is NULL')
            for db_entry in cursor:
                entry_urls = self.clean_urls(db_entry['homepage'])
                for homepage in entry_urls:
                    if '"' in homepage:
                        import ipdb
                        ipdb.set_trace()
                    netloc = scrapy.utils.url.parse_url(homepage).netloc
                    if not netloc:
                        homepage = "http://" + homepage
                    req = scrapy.Request(homepage, callback=self.parse_homepage, meta={'old_db_entry': db_entry})
                    yield req

    def parse_homepage(self, response):
        # push back all the urls
        # find if export // languages
        # langues = languages_in_page
        # fom angelList only

        in_links_extractor = LinkExtractor(allow=(response.url), unique=True)
        for link in in_links_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_homepage)

        item = Company()
        item['languages'] = self.get_languages(response)
        print item
        yield None
        """
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
        languages = set()
        # print self.all_tld_domains(response, out_links_extractor)
        tlds, _ = self.all_tld_domains(response)
        languages.update(tlds)

        query_string = scrapy.utils.url.parse_url(response.url).query
        query = scrapy.utils.url.parse_qsl(query_string)
        for _, val in query:
            if val in description_scraper.isocodes.languages:
                languages.add(val)

        # "?lang=en"
        # TODO this should be on all the text
        soup = BeautifulSoup(response.body)
        for lang in langdetect.detect_langs(soup.getText()):
            if lang.prob > 0.70:
                languages.add(lang.lang)

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
