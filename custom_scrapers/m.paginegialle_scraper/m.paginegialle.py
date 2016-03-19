# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import datetime
import random
import json

import itertools

import settings
import requests

from description_scraper.items import Business
from pipeline import DatabasePipeline


def get_or_default(obj, key, default):
    if key in obj:
        return obj[key]
    # print key, "failed"
    return default


def get_last_crawled_item():
    try:
        line = None
        with open("progress.log", "r") as plog:
            for line in plog:
                pass
            if line is None:
                raise IOError
        page_nr, category = line[:-1].split(",")
        page_nr = int(page_nr)
        print(datetime.datetime.now(), "resuming from ", page_nr)
    except IOError:
        page_nr = 1
        category = "none"
        print(datetime.datetime.now(), "resuming from ", page_nr, "no progress.log found")
    return page_nr, category


class PagineGialleSpider(object):
    def __init__(self):
        self.mapping = {'phones': 'phones', 'addresses': 'address', 'cities': 'city', 'countries': 'country',
                        'emails': 'emailAddress', 'pg_id': 'id', 'name': 'name', 'province': 'province',
                        'homepage': 'webAddress', 'zip': 'zip'}
        self.list_of_regions = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle D'aosta", "Veneto"]
        self.api_urls = [
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&what=%00&page={}&_={}",
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&address=%00&page={}&_={}"
            # "http://mobile.seat.it/searchpg?pagesize={}&where=Italia&sortby=name&output=jsonp&page={}&_={}",
            "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&lang=en&categories={}&where={}&page={}&_={}"
        ]
        self.cookies = {'s_vi': '[CS]v1|2AF274BE0531254E-400001050000BEF7[CE]',}
        self.headers = {'Pragma': 'no-cache', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
                        'Accept': '*/*', 'Referer': 'http://m.paginegialle.it/listing?what=formaggio&where=Italia',
                        'Connection': 'keep-alive', 'Cache-Control': 'no-cache',}
        self.pagesize = 999
        self.nr_parsed_items = None
        self.category = "unset"
        self.region = "unset"
        # self.pg_db_entries = 3541693
        # self.nr_parsed_items = 0

    def call_api(self, page_size, category, region, page):
        # fetches api json object
        while True:
            rnd = random.randrange(1000000000, 9999999999)
            time.sleep(settings.DOWNLOAD_DELAY)
            url = random.choice(self.api_urls)
            http_response = requests.get(url.format(page_size, category, region, page, rnd), headers=self.headers, cookies=self.cookies)
            print(url.format(page_size, category, region, page, rnd))
            try:
                json_response = json.loads(http_response.text[1:-3])
            except ValueError as e:
                # most likely error 500
                print(http_response.text, "err", e)
                time.sleep(60 * 5)
            else:
                # self.pg_db_entries = max(self.pg_db_entries, json_response['resultsNumber'])
                err, err_msg = self._verify_response(json_response)
                if not err:
                    return json_response, err_msg
                else:
                    import ipdb
                    ipdb.set_trace()
                    print("failed", (page, page_size), err_msg)

    def generate_requests(self):
        page_nr, resumed_category = get_last_crawled_item()
        self.category = resumed_category
        self.region = "undefined"

        # already_parsed_pages = self.nr_parsed_items / self.pagesize
        print("starting from {}/{}".format(page_nr, resumed_category))

        with open("categories.txt") as categories_list:
            if resumed_category != "none":
                while resumed_category != next(categories_list)[:-1]:
                    # scroll the file until we get our category
                    pass
                for i in itertools.count(page_nr):
                    # finish yielding page numbers
                    message = yield (self.pagesize, resumed_category, i)
                    if isinstance(message, StopIteration):
                        break

            # main loop
            for category in categories_list:
                category = category[:-1]
                self.category = category
                for region in self.list_of_regions:
                    self.region = region
                    for i in itertools.count(1):
                        message = yield (self.pagesize, category, region, i)
                        if isinstance(message, StopIteration):
                            break

    def parse_pg_search(self, search_results):
        print(datetime.datetime.now(), "category:", self.category, "region:", self.region, "page:",
              search_results['currentPage'], "results:", len(search_results['results']) * search_results['currentPage'],
              "/", search_results['resultsNumber'])

        for search_result in search_results['results']:
            item = Business()
            # self.nr_parsed_items += 1
            for k, v in self.mapping.items():
                item[k] = json.dumps(get_or_default(search_result, v, ''))
            yield item

    @staticmethod
    def _verify_response(search_results):

        required_keys = ['resultsNumber', 'results', 'currentPage', 'pagesize']
        for key in required_keys:
            if key not in search_results:
                return True, "{} not found".format(key)

        current_page = search_results['currentPage']
        page_size = search_results['pagesize']
        max_results = search_results['resultsNumber']

        page_end = current_page * page_size
        if page_end > max_results:
            page_begin = (current_page - 1) * page_size
            expected_results = page_begin - max_results
            last_page = True
        else:
            expected_results = page_size
            last_page = False

        if len(search_results['results']) != expected_results:
            return True, "found {} results expected {}".format(len(search_results['results']), expected_results)
        else:
            if last_page:
                return False, "last_page"
            else:
                return False, ""


def main():
    import pydevd
    import sys
    sys.path.append('/home/yitef/contact_list/pycharm-debug.egg')
    pydevd.settrace('localhost', port=31337, stdoutToServer=True, stderrToServer=True)

    spider = PagineGialleSpider()
    pipeline = DatabasePipeline()

    request_generator = spider.generate_requests()
    scraped_ids = set()

    for page_size, category, region, page_nr in request_generator:
        result_json, err_msg = spider.call_api(page_size, category, region, page_nr)
        for businessEntry in spider.parse_pg_search(result_json):
            if isinstance(businessEntry, Business):
                if businessEntry['pg_id'] in scraped_ids:
                    import ipdb; ipdb.set_trace()
                    print("duplicate")
                    break
                else:
                    scraped_ids.add(businessEntry['pg_id'])
                    pipeline.process_item(businessEntry)
            elif businessEntry is None:
                pass
            else:
                raise Exception("unhandled response")

        with open("progress.log", 'a') as plog:
            plog.write(str(page_nr) + "," + spider.category + "\n")
            plog.flush()
        if err_msg == "last_page":
            request_generator.send(StopIteration)
main()
