# -*- coding: utf-8 -*-
import scrapy
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import CompaniesRA
#from scrapy.spiders import CrawlSpider

class ReportAziendeSpider(CrawlSpider):
    name = "m.reportaziende.it"
    handle_httpstatus_list = [200]
    allowed_domains = ["reportaziende.it"]
    start_urls = [ "http://www.reportaziende.it/" ]

    def parse_companies:
        item = CompaniesRA()

        yield item

    def parse_w_links:
        for trgt in response.xpath("//ul[@class='carosello']/li/a/@href"):
        url = response.urljoin(trgt)
        yeld scrapy.Request(url, self.parse_companies)

    def parse(self, response):
        for trgt in response.xpath("///ul[@class='w_collegamenti']/li/a/@href").extract() :
            url = response.urljoin(trgt)
            yeld scrapy.Request(url, self.parse_w_collegamenti )




"""
def get_or_default(obj, key, default):
    if key in obj:
        return obj[key]
    # print key, "failed"
    return default


    def __init__(self, *a, **kw):
        super(PagineGialleSpider, self).__init__(*a, **kw)
        self.failed_requests = collections.deque([])
        self.request_url_lock = threading.Lock()

    def get_last_crawled_page(self):
        try:
            with open("progress.log","r") as plog:
                line = None
                for line in plog:
                        pass
                if line is None:
                    raise IOError
                last_page = int(line)
            print datetime.datetime.now(), "resuming from ", last_page
        except IOError:
            last_page = 1
            print datetime.datetime.now(), "resuming from ", last_page, "no progress.log found"
        return last_page

    def page_nr_iter(self,first_page, last_page):
        with open("progress.log","a") as plog:
            for page_nr in range(first_page, last_page):

                while True:
                    # retry the failed requests
                    try:
                        failed_request = self.failed_requests.pop()
                    except IndexError:
                        break
                    failed_page_nr = failed_request.meta['pg_page_nr']
                    yield page_nr
                with self.request_url_lock:
                    plog.write(str(page_nr)+"\n")
                    plog.flush()
                    yield page_nr

    def parse_search(self, response):
        search_results = json.loads(response.body[1:-3])

        def fail(msg):
            print  datetime.datetime.now(), response.meta['pg_page_nr'], msg
            #with open("err.log", "a") as err_log:
            #    err_log.write(response.url + "\n")
            self.failed_requests.append(scrapy.Request(response.url, callback=self.parse_search, meta={'pg_page_nr' : response.meta['pg_page_nr']}))
        if search_results['resultsNumber'] == 0:
            fail("search_results['resultsNumber'] == 0")
            yield None

        elif 'results' not in search_results:
            fail("results not found")
            yield None

        elif len(search_results['results']) != search_results['pagesize']:
            fail("found {} results expected {}".format(len(search_results['results']), search_results['pagesize']))

        else:
            print  datetime.datetime.now(), " ", search_results['currentPage'], "-> results:", len(search_results['results']), (search_results['currentPage']*99*100) / search_results['resultsNumber'], "%"
            for result in search_results['results']:
                item = Business()

                mapping = { 'phones': 'phones', 'addresses': 'address', 'cities': 'city', 'countries': 'country', 'emails': 'emailAddress', 'pg_id': 'id', 'name': 'name', 'province': 'province', 'homepage': 'webAddress', 'zip': 'zip' }
                for k,v in mapping.items():
                    item[k] = json.dumps(get_or_default(result, v, ''))
                yield item

    def parse_details(self, response):
        details_results = json.loads(response.body[1:-3])['detail']
        item = Business()

        item['pg_id'] = json.dumps(search_results['id'])
        item['meta_description'] = json.dumps(search_results['description'])

        yield item
"""
