import scrapy
import scrapy.spiders
import feedparser
import time
from scrapy import log
from media_monitor.items import MediaArticle


class RssFetcher(scrapy.spiders.XMLFeedSpider):
    name = 'rss_spider'
    # allowed_domains = ['example.com']
    # start_urls = ['http://www.example.com/feed.xml']
    iterator = 'iternodes' # This is actually unnecesary, since it's the default value
    itertag = 'item'

    def start_requests(self):
        rss_list = open("rss_list.csv")
        start_time = time.time()

        while True:
            for rss_url in rss_list:
                yield scrapy.Request(rss_url.rstrip(), self.parse)
            time_out = (5*60) - (time.time() - start_time)
            if time_out > 0:
                print "done; restarting in", time_out
                time.sleep(time_out)

    def parse_node(self, response, node):
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url, self.parse_news, meta=response.meta)

    def parse_news(self, response):
        item = MediaArticle()
        item['text'] = response.body
        item['url'] = response.url
        yield item
