import scrapy
import scrapy.spiders
import feedparser
import time
from media_monitor.items import MediaArticle


class RssFetcher(scrapy.spiders.XMLFeedSpider):
    name = 'rss_spider'
    # allowed_domains = ['example.com']
    # start_urls = ['http://www.example.com/feed.xml']
    iterator = 'iternodes' # This is actually unnecesary, since it's the default value
    itertag = 'item'

    def start_requests(self):

        while True:
            start_time = time.time()
            with open("rss_list.csv") as rss_list:
                for rss_url in rss_list:
                    yield scrapy.Request(rss_url.rstrip(), self.parse, dont_filter=True)
            time_out = (60*60) - (time.time() - start_time)
            import ipdb; ipdb.set_trace()
            self.crawler.stats.get_value('dupefilter/filtered')

            if time_out > 0:
                print "done; restarting in", time_out
                time.sleep(time_out)
            else:
                print "done; no timeout", time_out

    def parse_node(self, response, node):
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url, self.parse_news, meta=response.meta)

    def parse_news(self, response):
        item = MediaArticle()
        item['text'] = response.body
        item['url'] = response.url
        yield item
