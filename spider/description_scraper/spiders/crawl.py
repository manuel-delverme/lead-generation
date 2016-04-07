# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy.loader
import re
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

        types = ["srl", "snc", "sas", "spa", "sapa", "snc"]
        self.company_type_regexes = []
        for company_type in types:
            regex_str = "\s"
            for letter in company_type:
                regex_str += letter
                regex_str += "[\.\s]*"
            self.company_type_regexes.append(regex_str)

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
        if False:
            homepage = "http://www.amcolori.it"
            yield scrapy.Request(homepage, callback=self.parse_homepage, meta={'old_db_entry': None})
        else:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # cursor.execute('select * from "Businesses" where homepage != $$""$$ limit 100')  # crawl_time is NULL')
                cursor.execute('select DISTINCT * from "Businesses" where homepage != $$""$$ and pg_id != $$""$$ OFFSET floor(random()*12345) LIMIT 1;')  # crawl_time is NULL')
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

    def parse_deeper_page(self, response):
        item = Company()
        item['languages'] = self.get_languages(response)
        print item
        yield None

    def parse_homepage(self, response):
        # push back all the urls
        # find if export // languages
        # langues = languages_in_page
        # fom angelList only

        in_links_extractor = LinkExtractor(allow=(response.url), unique=True)
        for link in in_links_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_deeper_page)

        item = Company()
        item['languages'] = self.get_languages(response)
        item['title'] = self.get_name(response)
        print item
        yield None
        """
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
        page_txt = ''.join(self.get_page_text(response))
        try:
            detected_languages = langdetect.detect_langs(page_txt)
        except langdetect.lang_detect_exception.LangDetectException:
            return languages
        else:
            for lang in detected_languages:
                if lang.prob > 0.70:
                    languages.add(lang.lang)

        return languages

    def get_page_text(self, response):
        try:
            return response.meta['page_text']
        except KeyError:
            soup = BeautifulSoup(response.body)
            for elem in soup.findAll(['script', 'style']):
                elem.extract()
            text = map(unicode.lower, set(soup.getText().split("\n")))
            response.meta['page_text'] = text
            return text

    def get_name(self, response):
        name = None
        txt_arr = self.get_page_text(response)
        clean_txt = [re.sub(r'[^a-zA-Z0-9.\+\-]+', ' ', m) for m in txt_arr]
        # piva_matches = [txt for txt in txt_arr if re.search("p\.{0,1}\s*iva", txt) is not None]
        for txt in clean_txt:
            # piva_re = re.search("p\.{0,1}\s*iva\s*[0-9]+", match)
            # piva = piva_re.group()
            # code = int(re.search("[0-9]+", piva).group())
            # match = match[:piva.start()] + match[piva.end():]
            for company_type_regex in self.company_type_regexes:
                name = re.search("[\w\-\!]+" + company_type_regex, txt)
                if name:
                    name = name.group()
                    import ipdb; ipdb.set_trace()
                    print name
                    break
            if name:
                break

        if not name:
            print "fail all"
            last_name = response.meta['old_db_entry']['common_name']
            if last_name:
                # check if the old name is valid
                for company_type_regex in self.company_type_regexes:
                    name = re.search("[\w\-\!]+" + company_type_regex, last_name)
                    if name:
                        import ipdb; ipdb.set_trace()
                        name = name.group()
                        print "regex"
                    break
            if last_name and not name:
                print "old name is not valid, use it anyway"
                name = last_name
            if not name:
                import ipdb; ipdb.set_trace()
                print "last name is not present fallback to title"
                name = response.xpath("//title/text()").extract()
        return name

    def related_companies(self):
        # www.site.*
        # check DNS
        raise NotImplementedError
