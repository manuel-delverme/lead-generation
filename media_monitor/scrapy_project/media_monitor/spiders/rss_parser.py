import scrapy
import scrapy.spiders
import feedparser
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
        start_time = time.now()

        while True:
            for rss_url in rss_list:
                yield scrapy.Request(url, self.parse)
            time_out = 5*60 - (time.now() - start_time())
            time.sleep(time_out)

    def parse_node(self, response, node):
        log.msg('Hi, this is a <%s> node!: %s' % (self.itertag, ''.join(node.extract())))

        item = Item()
        item['id'] = node.select('@id').extract()
        item['name'] = node.select('name').extract()
        item['description'] = node.select('description').extract()
        return item

    def parse_node(self, response, node):
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url, self.parse_news, meta=response.meta)

    def parse_news(self, response):
        item = MediaArticle()
        # only log the warning info from request
        logging.getLogger("requests").setLevel(logging.WARNING)
	import ipdb; ipdb.set_trace()

	"""
        # use newspaper-0.0.8 to scrape the webpage, then get clean text.
        article = Article(response.url, lang="it")
        article.download(html=response.body)
        article.parse()

        item['link'] = article.url
        item['title'] = article.title
        # item['text'] = article.text
        item['authors'] = article.authors
        item['date'] = article.publish_date
        # item['domain'] = response.meta['topic']

        article.additional_data['words'] = set(newspaper.nlp.split_words(article.text))

        for businessName in open("static_names.csv"):
            businessName = businessName.strip("\n")
            if businessName in article.additional_data['words']:
                print("{},{}\n".format(businessName, article.url))
                article.nlp()
                with open("results.log", "a") as output:
                    output.write("{},{}\n".format(businessName, article.url))
                item['summary'] = article.summary
                yield item
	"""
