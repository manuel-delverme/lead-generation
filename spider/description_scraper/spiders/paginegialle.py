# -*- coding: utf-8 -*-
import logging
import scrapy
import json
import requests
import itertools
from extruct.w3cmicrodata import MicrodataExtractor

from description_scraper.items import Business
from scrapy.spiders import CrawlSpider


class PagineGialleSpider(CrawlSpider):
    sitemap_urls = [ "http://www.paginegialle.it/sitemap_schedeazienda_86.xml.gz", ]
    # sitemap_urls = ["http://localhost/sitemap_schedeazienda_86.xml.gz"]
    name = "m.paginegialle.it"
    handle_httpstatus_list = [200]

    def start_requests(self):

        search_url = "http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize=99&output=jsonp"

        page = 1
        response = requests.get(search_url)
        search_url += "&page={}"
        response_json = json.loads(response.text[1:-3])
        last_page = response_json['lastPage']

        with open("progress.log","w") as plog:
            for page in range(1, last_page + 1):
                plog.write(str(page))
                plog.flush()
                yield scrapy.Request(search_url.format(page), callback=self.parse_search)
        """
        details_url = "http://mobile.seat.it/detailpg?output=jsonp&client=pgbrowsing&id={}&version=5.0.1&device=evo"
        for pg_id in select_where_pg_id_and_not_categories:
            yield scrapy.Request(url.format(pg_id), callback=self.parse_details)
        """

    def __init__(self, *a, **kw):
        super(PagineGialleSpider, self).__init__(*a, **kw)

    def parse_search(self, response):
        import ipdb; ipdb.set_trace()
        search_results = json.loads(response.body[1:-3])
        # response_json['filters']
        for result in search_results['results']:
            item = Business()

            item['phones'] = json.dumps(result['phones'])
            item['addresses'] = json.dumps(result['address'])
            item['cities'] = json.dumps(result['city'])
            item['countries'] = json.dumps(result['country'])
            item['emails'] = json.dumps(result['email'])
            item['pg_id'] = json.dumps(result['id'])
            item['name'] = json.dumps(result['name'])
            item['province'] = json.dumps(result['province'])
            item['homepage'] = json.dumps(result['webAddress'])
            item['zip'] = json.dumps(result['zip'])

            yield item

    def parse_details(self, response):
        details_results = json.loads(response.body[1:-3])['detail']
        item = Business()

        item['pg_id'] = json.dumps(search_results['id'])
        item['meta_description'] = json.dumps(search_results['description'])

        yield item
