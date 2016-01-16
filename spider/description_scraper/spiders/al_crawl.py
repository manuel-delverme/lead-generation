# -*- coding: utf-8 -*-
import scrapy
import psycopg2


class CrawlSpider(scrapy.Spider):
    handle_httpstatus_list = [404]
    name = 'alCrawler'
    def __init__(self):
        connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "localhost", "write_only")
        self._conn = psycopg2.connect(connect_string)

        self.cookies = {
            '_angellist': 'b05ff44e07344842afcf6c8b4bc42bdc',
            'visitor_hash': '60bc521cd38a722e854b20ee56f4fcd7',

        }
        self.headers = { 
            'Origin': 'https://angel.co',
            'Accept-Encoding': 'gzip, deflate',
            'X-CSRF-Token': 'A27YmVOFY25xH0dbN6Pk0BicNQuw5yvrZLmMzcZosR8=',
            'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'https://angel.co/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'DNT': '1',
        }


    def start_requests(self):
        with self._conn.cursor() as cursor:
            cursor.execute('select angel_link from "Businesses" where angel_id is not NULL and crawl_time is NULL')
            for url, in cursor:
                # url = url[:4] + url[5:]
                yield scrapy.Request(url = url + "/", cookies=self.cookies, headers=self.headers)

    def parse(self, response):
        import ipdb; ipdb.set_trace()
        raise Exception()
