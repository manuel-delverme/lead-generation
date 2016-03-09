# -*- coding: utf-8 -*-
import threading
import time
import datetime
import random
import json
import requests
# import logging
# import scrapy
# from extruct.w3cmicrodata import MicrodataExtractor
import collections
import scrapy.http.response
import scrapy.http.request

from description_scraper.items import Business
from scrapy.spiders import CrawlSpider


def get_or_default(obj, key, default):
    if key in obj:
        return obj[key]
    # print key, "failed"
    return default


def get_last_crawled_page():
    try:
        line = None
        with open("progress.log", "r") as plog:
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


class PagineGialleSpider(CrawlSpider):
    name = "m.paginegialle.it"
    handle_httpstatus_list = [200]

    def __init__(self, *a, **kw):
        super(PagineGialleSpider, self).__init__(*a, **kw)
        self.failed_requests = collections.deque([])
        self.request_url_lock = threading.Lock()

    def page_nr_iter(self, first_page, last_page):
        with open("progress.log", 'a') as plog:
            for page_nr in range(first_page, last_page):
                while True:
                    # retry the failed requests
                    try:
                        failed_request = self.failed_requests.pop()
                        page_nr = failed_request.meta['pg_page_nr']
                        yield page_nr
                    except IndexError:
                        break
                plog.write(str(page_nr) + "\n")
                plog.flush()
                yield page_nr

    def start_requests(self):
        search_url = "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize=99&output=jsonp&what=%00&page={}&_={}"

        rnd = random.randrange(1000000000, 9999999999)
        print "downloading pg info"

        while True:
            initial_response = requests.get(search_url.format(1, rnd))
            try:
                statistics_json = json.loads(initial_response.text[1:-3])
            except ValueError as e:
                print initial_response.text
                print "err", e
                time.sleep(60 * 5)
                continue
            err, err_msg = self._verify_response(statistics_json)
            if not err:
                break
            else:
                self._fail(response, err_msg, retry=False)

        first_page = get_last_crawled_page()
        last_page = statistics_json['lastPage']
        print "found {} pages".format(last_page)
        print "starting from {}".format(first_page)

        # main loop
        for page_nr in self.page_nr_iter(first_page, last_page):
            rnd = random.randrange(10000000000, 99999999999)

            req = scrapy.http.request.Request(search_url.format(page_nr, rnd), callback=self.parse_search)
            req.meta['pg_page_nr'] = page_nr
            yield req

    def parse_search(self, http_response):
        search_results = json.loads(http_response.body[1:-3])

        err, err_msg = self._verify_response(search_results)
        if err:
            self._fail(http_response, err_msg)
            yield None
        else:
            print search_results['currentPage']
            print search_results['pagesize']
            print search_results['resultsNumber']

            perc = 100 * (
                (search_results['currentPage'] * search_results['pagesize']) / search_results['resultsNumber'])
            print  datetime.datetime.now(), search_results['currentPage'], "-> results:", len(
                search_results['results']), perc, "%"

            for result in search_results['results']:
                item = Business()

                mapping = {'phones': 'phones', 'addresses': 'address', 'cities': 'city', 'countries': 'country',
                           'emails': 'emailAddress', 'pg_id': 'id', 'name': 'name', 'province': 'province',
                           'homepage': 'webAddress', 'zip': 'zip'}
                for k, v in mapping.items():
                    item[k] = json.dumps(get_or_default(result, v, ''))
                yield item

    def _fail(self, response, msg, retry=True):
        if hasattr(response.request, 'meta'):
            resp_id = response.request.meta['pg_page_nr']
        else:
            resp_id = "NO ID FOUND"
        print  datetime.datetime.now(), resp_id, msg
        if retry:
            failed_request = scrapy.http.request.Request(response.url, callback=self.parse_search,
                                                         meta={'pg_page_nr': response.request.meta['pg_page_nr']})
            self.failed_requests.append(failed_request)

    @staticmethod
    def _verify_response(search_results):
        if 'resultsNumber' not in search_results:
            return False, "resultsNumber not found"
        elif search_results['resultsNumber'] < 3000000:
            return False, "{} results, too few".format(search_results['resultsNumber'])
        elif 'results' not in search_results:
            return False, "results not found"
        elif len(search_results['results']) != search_results['pagesize']:
            return False, "found {} results expected {}".format(len(search_results['results']),
                                                                search_results['pagesize'])
        else:
            print "search_results['resultsNumber']", search_results['resultsNumber']
            print "found {} results expected {}".format(len(search_results['results']), search_results['pagesize'])
            return True, ""

    @staticmethod
    def parse_details(json_entry):
        details_results = json.loads(json_entry.body[1:-3])['detail']
        item = Business()

        item['pg_id'] = json.dumps(details_results['id'])
        item['meta_description'] = json.dumps(details_results['description'])

        yield item


spider = PagineGialleSpider()
for request in spider.start_requests():
    result = request

    while isinstance(result, scrapy.http.request.Request):
        response = requests.get(request.url)
        response = scrapy.http.HtmlResponse(body=response.text, request=request, encoding="UTF-8", url=response.url)
        for result in request.callback(response):
            if isinstance(result, Business):
                print "# persist(result)"
            elif result is None:
                pass
            else:
                raise Exception("unhandled response")
