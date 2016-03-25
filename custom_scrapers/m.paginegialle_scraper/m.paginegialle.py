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
    return default


def get_last_crawled_item():
    try:
        line = None
        with open("progress.log", "r") as plog:
            for line in plog:
                pass
            if line is None:
                raise IOError
        page_nr, category = line.strip("\n").split(",")
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
        self.list_of_regions = ["Sicilia", "Molise", "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli Venezia Giulia", "Lazio", "Liguria",
                                "Lombardia", "Marche", "Piemonte", "Puglia", "Sardegna", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle D'aosta", "Veneto"]
        self.api_urls = [
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&what=%00&page={}&_={}",
            # "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&address=%00&page={}&_={}"
            # "http://mobile.seat.it/searchpg?pagesize={}&where=Italia&sortby=name&output=jsonp&page={}&_={}",
            "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize={}&output=jsonp&lang=en&categories={}&where={}&page={}&_={}"
        ]
        self.cookies = {'s_vi': '[CS]v1|2AF274BE0531254E-400001050000BEF7[CE]'}
        self.headers = {'Pragma': 'no-cache', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
                        'Accept': '*/*', 'Referer': 'http://m.paginegialle.it/listing?what=formaggio&where=Italia',
                        'Connection': 'keep-alive', 'Cache-Control': 'no-cache'}
        self.pagesize = settings.PAGE_SIZE
        self.nr_parsed_items = None
        self.category = "unset"
        self.region = "unset"
        self.IGNORE = False
        # self.pg_db_entries = 3541693
        # self.nr_parsed_items = 0

    def call_api(self, page_size, category, region, page):
        # fetches api json object
        while True:
            rnd = random.randrange(1000000000, 9999999999)
            url = random.choice(self.api_urls)
            time.sleep(settings.DOWNLOAD_DELAY)
            # print(url.format(page_size, category, region, page, rnd))
            http_response = requests.get(url.format(page_size, category, region, page, rnd), headers=self.headers, cookies=self.cookies)
            try:
                json_response = json.loads(http_response.text[1:-3])
            except ValueError as e:
                # most likely error 500
                print(http_response.text, "err", e)
                print(page_size, category, region, page, rnd)
                time.sleep(60 * 5)
            else:
                # self.pg_db_entries = max(self.pg_db_entries, json_response['resultsNumber'])
                err, err_msg = self._verify_response(json_response)
                if not err:
                    return json_response, err_msg
                else:
                    if err_msg == "results not found":
                        with open(settings.FAIL_LOG, 'a') as fail_log:
                            fail_log.write("{},{},{},{}\n".format(page_size, category, region, page))
                        return None, err_msg
                    else:
                        print("failed", (page_size, category, region, page), err_msg)

    def generate_requests(self):
        page_nr, resumed_category = get_last_crawled_item()
        self.category = resumed_category
        self.region = "undefined"

        # already_parsed_pages = self.nr_parsed_items / self.pagesize
        print("starting from {}/{}".format(page_nr, resumed_category))

        def iterate_category(category, initial_page=1):
            category = category.strip("\n")
            self.category = category
            for region in self.list_of_regions:
                self.region = region
                for i in itertools.count(initial_page):
                    status = yield self.pagesize, category, region, i
                    if status == "change region":
                        yield
                        break

        for failed_record in open(settings.RESUME_LOG):
            page_tuple = tuple(failed_record.strip("\n").split(","))
            self.category = page_tuple[1]
            self.region = page_tuple[2]
            yield page_tuple

        with open("categories.txt") as categories_list:
            if resumed_category != "none":
                while resumed_category != next(categories_list).strip("\n"):
                    # scroll the file until we get our category
                    pass
                interrupted_iter = iterate_category(resumed_category, page_nr)
                for page_tuple in interrupted_iter:
                    status = yield page_tuple
                    if status is not None:
                        interrupted_iter.send(status)
                        yield

            # main loop
            for category in categories_list:
                tuples_iter = iterate_category(category, page_nr)
                for page_tuple in tuples_iter:
                    status = yield page_tuple
                    if status is not None:
                        tuples_iter.send(status)
                        yield

    def parse_pg_search(self, search_results):
        if search_results is None:
            yield None
        else:
            print(datetime.datetime.now(), "category:", self.category, "region:", self.region, "page:",
                  search_results['currentPage'], "results:", len(search_results['results']) * search_results['currentPage'],
                  "/", search_results['resultsNumber'])

            for search_result in search_results['results']:
                item = Business()
                # self.nr_parsed_items += 1
                for k, v in self.mapping.items():
                    item[k] = json.dumps(get_or_default(search_result, v, ''))
                yield item

    def _verify_response(self, search_results):
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
            expected_results = max_results - page_begin
            last_page = True
        else:
            expected_results = page_size
            last_page = False

        found_results = len(search_results['results'])

        if page_end > 4900:
            return False, "last_page"
        if found_results != expected_results:
            if float(expected_results - found_results) / float(max_results) < 0.15:
                print("found {} results expected {} ignoring the diff".format(found_results, expected_results))
                # with open(settings.FAIL_LOG, 'a') as fail_log:
                #     fail_log.write("{},{},{},{}\n".format(page_size, search_results['request']['params']['params']['categories'], search_results['request']['params']['params']['where'], current_page))
                return False, "last_page"
            elif float(expected_results - found_results) / float(max_results) < 0.30:
                if last_page:
                    print("found {} results expected {} ignoring the diff FUCKTHIS".format(found_results, expected_results))
                    with open(settings.FAIL_LOG, 'a') as fail_log:
                        fail_log.write("{},{},{},{}\n".format(page_size, search_results['request']['params']['params']['categories'], search_results['request']['params']['params']['where'], current_page))
                    return False, "last_page"
            else:
                return True, "found {} results expected {}".format(found_results, expected_results)
        else:
            if last_page:
                return False, "last_page"
            else:
                return False, ""


def main():
    spider = PagineGialleSpider()
    pipeline = DatabasePipeline()

    request_generator = spider.generate_requests()
    scraped_ids = set()

    for page_size, category, region, page_nr in request_generator:
        result_json, err_msg = spider.call_api(page_size, category, region, page_nr)
        if result_json is None:
            print("no results; change region ({})".format((page_size, category, region, page_nr)))
            with open("failed.log", 'a') as fail_log:
                fail_log.write("{},{},{},{}\n".format(page_size, category, region, page_nr))
            request_generator.send("change region")
            continue
        else:
            duplicates = 0
            for businessEntry in spider.parse_pg_search(result_json):
                if isinstance(businessEntry, Business):
                    if businessEntry['pg_id'] in scraped_ids:
                        duplicates += 1
                    else:
                        scraped_ids.add(businessEntry['pg_id'])
                        pipeline.process_item(businessEntry)
                elif businessEntry is None:
                    continue
                else:
                    raise Exception("unhandled response")

            if duplicates > 0:
                print("{} duplicates".format(duplicates))
                with open(settings.FAIL_LOG, 'a') as fail_log:
                    fail_log.write("{},{},{},{}\n".format(page_size, category, region, page_nr))

            with open("progress.log", 'a') as plog:
                plog.write(str(page_nr) + "," + spider.category + "\n")
                plog.flush()
            if err_msg == "last_page":
                request_generator.send("change region")
main()
