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
        start_time = time.time.now()

        while True:
            for rss_url in rss_list:
                yield scrapy.Request(url, self.parse)
            time_out = (5*60) - (time.time.now() - start_time)
            time.sleep(time_out)

    def parse_node(self, response, node):
        log.msg('Hi, this is a <%s> node!: %s' % (self.itertag, ''.join(node.extract())))
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url, self.parse_news, meta=response.meta)

