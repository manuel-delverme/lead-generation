# -*- coding: utf-8 -*-
import threading
import logging
import time
import datetime
import scrapy
import random
import json
import requests
import itertools
import collections
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import CrawlSpider

def get_or_default(obj, key, default):
    if key in obj:
        return obj[key]
    # print key, "failed"
    return default


class PagineGialleSpider(CrawlSpider):
    name = "m.paginegialle.it"
    handle_httpstatus_list = [200]

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


    def start_requests(self):
        search_url = "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize=99&output=jsonp&what=%00&page={}&_={}"

        rnd = random.randrange(1000000000,9999999999)
        print "downloading pg info"
        response = requests.get(search_url.format(1, rnd))


        response_json = None
        while response_json is None:
            try:
                response_json = json.loads(response.text[1:-3])
            except ValueError as e:
                print response.text
                print "err", e

                time.sleep(60*5)

        first_page = self.get_last_crawled_page()
        last_page = response_json['lastPage']
        print "found {} pages".format(last_page)
        print "starting from {}".format(first_page)

        for page_nr in self.page_nr_iter(first_page, last_page):
            rnd = random.randrange(10000000000, 99999999999)

            req = scrapy.Request(search_url.format(page_nr, rnd), callback=self.parse_search)
            req.meta['pg_page_nr'] = page_nr
            yield req

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
