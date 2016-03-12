# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import datetime
import random
import json

import itertools

import settings
import requests
import collections
import scrapy.http.response
import scrapy.http.request

from description_scraper.items import Business
from scrapy.spiders import CrawlSpider
from pipeline import DatabasePipeline


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
        print(datetime.datetime.now(), "resuming from ", last_page)
    except IOError:
        last_page = 0
        print(datetime.datetime.now(), "resuming from ", last_page, "no progress.log found")
    return last_page


class PagineGialleSpider():
    name = "m.paginegialle.it"

    def __init__(self):
        self.api_urls = [
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&what=%00&page={}&_={}",
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&address=%00&page={}&_={}"
            "http://mobile.seat.it/searchpg?pagesize={}&where=Italia&sortby=name&output=jsonp&page={}&_={}",
        ]
        self.cookies = { 's_vi': '[CS]v1|2AF274BE0531254E-400001050000BEF7[CE]', }
        self.headers = { 'Pragma': 'no-cache', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'en-US,en;q=0.8,it;q=0.6', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36', 'Accept': '*/*', 'Referer': 'http://m.paginegialle.it/listing?what=formaggio&where=Italia', 'Connection': 'keep-alive', 'Cache-Control': 'no-cache', }
        self.MAX_PAGESIZE = 99999
        self.MIN_PAGESIZE = 80
        self.pagesize = 999
        self.pg_db_entries = 3541693
        self.nr_parsed_items = 0

    def page_nr_iter(self, already_parsed_items):
        # controls request progress and calculates what to download next
        self.nr_parsed_items = already_parsed_items
        while True:
            page_size = min(max(self.nr_parsed_items, self.MIN_PAGESIZE), self.MAX_PAGESIZE)
            page_nr = int(self.nr_parsed_items / page_size)
            yield (page_size, page_nr)

    def call_api(self, page_size, page):
        # fetches api json object
        while True:
            rnd = random.randrange(1000000000, 9999999999)
            time.sleep(settings.DOWNLOAD_DELAY)
            url = random.choice(self.api_urls)
            http_response = requests.get(url.format(page_size, page, rnd), headers=self.headers, cookies=self.cookies)
            try:
                json_response = json.loads(http_response.text[1:-3])
            except ValueError as e:
                # most likely error 500
                print(http_response.text, "err", e)
                time.sleep(60 * 5)
            else:
                self.pg_db_entries = max(self.pg_db_entries, json_response['resultsNumber'])
                err, err_msg = self._verify_response(json_response)
                if not err:
                    return json_response
                else:
                    print("failed", (page, page_size), err_msg)

    def generate_requests(self):
        self.nr_parsed_items = get_last_crawled_page()

        already_parsed_pages = self.nr_parsed_items / self.pagesize
        print("starting from {}".format(self.nr_parsed_items))

        # main loop
        for page_nr in itertools.count(already_parsed_pages):
            yield (self.pagesize, page_nr)

        for page_size, page_nr in self.page_nr_iter(self.nr_parsed_items):
            yield (page_size, page_nr)

    def parse_pg_search(self, search_results):
        # turns json object in items
        perc = 100 * (self.nr_parsed_items / self.pg_db_entries)
        print(datetime.datetime.now(), "progress:", self.nr_parsed_items, "results:", len(search_results['results']), "/", search_results['pagesize'], perc, "%")

        for search_result in search_results['results']:
            item = Business()
            mapping = {'phones': 'phones', 'addresses': 'address', 'cities': 'city', 'countries': 'country', 'emails': 'emailAddress', 'pg_id': 'id', 'name': 'name', 'province': 'province', 'homepage': 'webAddress', 'zip': 'zip'}
            self.nr_parsed_items += 1
            for k, v in mapping.items():
                item[k] = json.dumps(get_or_default(search_result, v, ''))
            yield item
        with open("progress.log", 'a') as plog:
            plog.write(str(self.nr_parsed_items) + "\n")
            plog.flush()

    @staticmethod
    def _verify_response(search_results):
        if 'resultsNumber' not in search_results:
            return True, "resultsNumber not found"
        elif search_results['resultsNumber'] < 3000000/search_results['pagesize']:
            return True, "{} results, too few".format(search_results['resultsNumber'])
        elif 'results' not in search_results:
            return True, "results not found"
        elif len(search_results['results']) == 0:  # search_results['pagesize']:
            return True, "found {} results expected {}".format(len(search_results['results']),
                                                               search_results['pagesize'])
        else:
            return False, ""


def main():
    spider = PagineGialleSpider()
    pipeline = DatabasePipeline()

    for page_size, page_nr in spider.generate_requests():
        result_json = spider.call_api(page_size, page_nr)
        for businessEntry in spider.parse_pg_search(result_json):
            if isinstance(businessEntry, Business):
                pipeline.process_item(businessEntry)
            elif businessEntry is None:
                pass
            else:
                raise Exception("unhandled response")
main()
