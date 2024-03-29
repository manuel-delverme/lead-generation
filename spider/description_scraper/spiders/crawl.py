# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy.loader
import re
import psycopg2
import psycopg2.extras
import itertools
from ..settings import DATABASE
import langdetect
import description_scraper.isocodes
import tldextract
import scrapy.utils.url
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from description_scraper.items import Company
import nltk


class OutOfUrls(Exception):
    pass

class CrawlSpider(scrapy.Spider):
    name = "website_crawler"

    def __init__(self, **kwargs):
        super(CrawlSpider, self).__init__(**kwargs)
        self.ignoreBreakpoint = ["failed to find in html and no record present"]
        connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", DATABASE['password'])
        self._conn = psycopg2.connect(connect_string)

        types = ["srl", "snc", "sas", "spa", "sapa", "snc"]
        self.company_type_regexes = []
        for company_type in types:
            regex_str = "\s"
            for letter in company_type:
                regex_str += letter
                regex_str += "[\.\s]*"
            self.company_type_regexes.append(regex_str)
        self.cached_stopwords = dict()

    def clean_stopwords(self, text, languages):
        stopwords = set()

        language_map = {
            'it': 'italian',
            'en': 'english',
            'de': 'german'
        }
        try:
            languages = [language_map[l] for l in languages]
        except KeyError:
            import ipdb; ipdb.set_trace()
            print "language not mapped yet"

        for language in languages:
            try:
                stopwords.update(self.cached_stopwords[language])
            except KeyError:
                self.cached_stopwords[language] = set(nltk.corpus.stopwords.words(language))
                stopwords.update(self.cached_stopwords[language])

        text = text.lower()
        # tokens = RegexpTokenizer(r'\w+').tokenize(text)
        tokens = nltk.word_tokenize(text)
        filtered_words = filter(lambda token: token not in stopwords, tokens)
	return ' '.join(filtered_words)

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
                if "entry_urls is fucked up" not in self.ignoreBreakpoint:
                    import ipdb; ipdb.set_trace()
                    print "entry_urls is fucked up"

        if entry_urls is None:
            if "entry_urls is None" not in self.ignoreBreakpoint:
                import ipdb; ipdb.set_trace()
                print "entry_urls is None"

        entry_urls = [remove_serialization(url) for url in entry_urls]
        return entry_urls

    def fetch_rows(self, lower, batch_size):
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # cursor.execute('select * from "Businesses" where homepage != $$""$$ and pg_id != $$""$$ and id > 6159270 order by id OFFSET %(lower)s LIMIT %(size)s;', {'lower': lower, 'size': batch_size})
            cursor.execute('SELECT * FROM "Businesses" order by id OFFSET %(lower)s LIMIT %(size)s;', {'lower': lower, 'size': batch_size})
            # cursor.execute('select 1')
            if not cursor.rowcount:
                raise OutOfUrls
            for db_entry in cursor:
                entry_urls = self.clean_urls(db_entry['homepage'])
                for homepage in entry_urls:
                    if '"' in homepage:
                        if "bad formatting" not in self.ignoreBreakpoint:
                            import ipdb; ipdb.set_trace()
                            print "bad formatting"
                    netloc = scrapy.utils.url.parse_url(homepage).netloc
                    if not netloc:
                        homepage = "http://" + homepage
                    req = scrapy.Request(homepage, callback=self.parse, meta={'old_db_entry': db_entry})
                    yield req

    def start_requests(self):
        batch_size = 100
        for step in itertools.count():
            lower = step * batch_size
            try:
                for request in self.fetch_rows(lower, batch_size):
                    yield request
            except OutOfUrls:
                return

    def parse(self, response):
        # push back all the urls
        # find if export // languages
        # langues = languages_in_page
        # fom angelList only

        if not hasattr(response, 'body_as_unicode'):
            yield None
        homepage_url = self.clean_urls(response.meta['old_db_entry']['homepage'])[0]
        in_links_extractor = LinkExtractor(allow=(homepage_url), unique=True)
        for link in in_links_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse, meta=response.request.meta)

        item = Company()
        item['languages'] = self.get_languages(response)
        item['formal_name'] = self.get_name(response, item['languages'])

        item['peer_companies'] = self.peer_companies(response)
        item['crawled_url'] = response.url
        item['depth'] = response.meta['depth']
        item['description'] = self.get_description(response)
        item['keywords'] = self.get_keywords(response)
        item['body'] = response.body

        # values to forward from the old db
        forward_values = [
            'homepage',
            'addresses',
            'revenue',
            'phones',
            'employees_max',
            # 'common_name',
            'funding',
            'zip',
            # 'formal_name',
            'angel_id',
            'employees_min',
            'angel_link',
            'province',
            'cities',
            'emails',
            'countries',
            'pg_id'
        ]
        for key in forward_values:
            item[key.replace("angel", "al")] = response.request.meta['old_db_entry'][key]
        yield item

    def get_description(self, response):
        # TODO add og, twitter etc
        return json.dumps(
            response.xpath("//meta[@name='description']/@content").extract()
        )

    def get_keywords(self, response):
        # TODO add og, twitter etc
        return json.dumps(
            response.xpath("//meta[@name='keywords']/@content").extract()
        )

    def peer_companies(self, response):
        # www.site.*
        # netloc = scrapy.utils.url.parse_url(response.url).netloc
        extraction = tldextract.extract(response.url)
        domain = extraction.domain
        # TODO: check DNS
        tld_domains = [domain + "." + tld for tld in self.all_tld_domains(response)[0]]
        try:
            tld_domains.remove(extraction.registered_domain)
        except ValueError:
            pass
        return tld_domains

    def all_tld_domains(self, response):
        out_links_extractor = LinkExtractor(deny=(response.meta['old_db_entry']['homepage']), unique=True)
        tlds = []
        not_tlds = []
        # netloc = scrapy.utils.url.parse_url(response.url).netloc
        # basedomain = netloc[:netloc.rindex(".")]
        domain = tldextract.extract(response.url).domain

        for link in out_links_extractor.extract_links(response):
            link_url = tldextract.extract(link.url)
            if link_url.domain == domain:
                tlds.append(link_url.suffix)
            else:
                not_tlds.append(link_url.registered_domain)
        return set(tlds), set(not_tlds)

    def get_languages(self, response):
        languages = set()
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

    def match_company_types(self, text, languages):
        # piva_re = re.search("p\.{0,1}\s*iva\s*[0-9]+", match)
        # piva = piva_re.group()
        # code = int(re.search("[0-9]+", piva).group())
        # match = match[:piva.start()] + match[piva.end():]
        # text = self.clean_stopwords(text, languages)
        for company_type_regex in self.company_type_regexes:
            # get everything before the company_type
            name_match = re.search("[\s\w\,\.]+" + company_type_regex + "[\.\s\b]", text)
            if name_match:
                name = name_match.group()
                return name

    def get_name(self, response, languages):
        txt_arr = self.get_page_text(response)
        clean_txt = {re.sub(r'[^a-zA-Z0-9.\+\-]+', ' ', m) for m in txt_arr}
        # piva_matches = [txt for txt in txt_arr if re.search("p\.{0,1}\s*iva", txt) is not None]

        company_type_matches = filter(None, [self.match_company_types(txt, languages) for txt in clean_txt])
        if len(company_type_matches) == 1:
            return company_type_matches[0]
        else: # fallback
            try:
                name = response.meta['old_db_entry']['common_name']
                assert name is not None
                return name
            except (KeyError, AssertionError) as e:
                names =  response.xpath("//title/text()").extract()
                if len(names) > 0:
                    return names[0]
                else:
                    extraction = tldextract.extract(response.url)
                    return extraction.domain
