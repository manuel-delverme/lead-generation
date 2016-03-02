# -*- coding: utf-8 -*-
import logging
import time
import scrapy
import random
import json
import requests
import itertools
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import CrawlSpider

def get_or_default(obj, key, default):
    if key in obj:
        return obj[key]
    print key, "failed"
    return default


class PagineGialleSpider(CrawlSpider):
    name = "m.paginegialle.it"
    handle_httpstatus_list = [200]

    def start_requests(self):

        search_url = "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize=99&output=jsonp&what=%00&_={}"

        page = 1
        rnd = random.randrange(10000000000,99999999999)
        response = requests.get(search_url.format(rnd))
        search_url += "&page={}"

        response_json = json.loads(response.text[1:-3])
        last_page = response_json['lastPage']

        with open("progress.log","w") as plog:
            for page in range(670, last_page + 1):
                plog.write(str(page)+"\n")
                plog.flush()
                rnd = random.randrange(10000000000,99999999999)
                yield scrapy.Request(search_url.format(rnd,page), callback=self.parse_search)
        """
        details_url = "http://mobile.seat.it/detailpg?output=jsonp&client=pgbrowsing&id={}&version=5.0.1&device=evo"
        for pg_id in select_where_pg_id_and_not_categories:
            yield scrapy.Request(url.format(pg_id), callback=self.parse_details)
        """

    def __init__(self, *a, **kw):
        super(PagineGialleSpider, self).__init__(*a, **kw)

    def parse_search(self, response):
        search_results = json.loads(response.body[1:-3])
        
        if search_results['resultsNumber'] == 0:
            # time.sleep(5)
            print "search_results['resultsNumber'] == 0"
            yield scrapy.Request(response.url, callback=self.parse_search)
        elif 'results' not in search_results:
            # time.sleep(5)
            print "results missing"
            yield scrapy.Request(response.url, callback=self.parse_search)
        else:
            print (search_results['currentPage']*99*100) / search_results['resultsNumber'], "%"
            for result in search_results['results']:
                item = Business()

                mapping = {
                    'phones': 'phones',
                    'addresses': 'address',
                    'cities': 'city',
                    'countries': 'country',
                    'emails': 'emailAddress',
                    'pg_id': 'id',
                    'name': 'name',
                    'province': 'province',
                    'homepage': 'webAddress',
                    'zip': 'zip'
                }
                for k,v in mapping.items():
                    item[k] = json.dumps(get_or_default(result, v, ''))
                yield item

    def parse_details(self, response):
        details_results = json.loads(response.body[1:-3])['detail']
        item = Business()

        item['pg_id'] = json.dumps(search_results['id'])
        item['meta_description'] = json.dumps(search_results['description'])

        yield item
