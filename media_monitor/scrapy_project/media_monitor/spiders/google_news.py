import scrapy
import scrapy.spiders
from media_monitor.items import MediaArticle
import logging
from newspaper import Article


class GoogleNewsCrawler(scrapy.Spider):
    name = "GoogleNews"

    def __init__(self):
        self.google_news_topics = {
            'w': 'Esteri',
            'n': 'Italia',
            'b': 'Economia',
            'tc': 'Scienza e tecnologia',
            'e': 'Intrattenimento',
            's': 'Sport',
            'm': 'Salute'
        }

    def start_requests(self):
        for topic in self.google_news_topics.keys():
            url = "https://news.google.it/news/section?cf=all&pz=1&ned=us&topic={}".format(topic)
            yield scrapy.Request(url, self.parse, meta={'topic': topic})

    baseURL = "https://news.google.com"
    allowed_domains = ["news.google.com"]

    def parse(self, response):
        for href in response.xpath('//div[@class="moreLinks"]/a/@href').extract():
            full_url = self.baseURL + href
            yield scrapy.Request(full_url, callback=self.parse_news)

    def parse_news(self, response):
        item = MediaArticle()
        # only log the warning info from request
        logging.getLogger("requests").setLevel(logging.WARNING)

        for href in response.xpath('//h2[@class="title"]/a/@href').extract():
            # use newspaper-0.0.8 to scrape the webpage, then get clean text.
            article = Article(item['link'])
            article.download()
            article.parse()
            article.nlp()

            item['link'] = href
            item['title'] = article.title
            item['summary'] = article.summary
            item['text'] = article.text
            # item['authors'] = article.authors
            # item['date'] = article.publish_date
            item['domain'] = response.meta['topic']
            for businessName in open("static_names.csv").readlines():
                if businessName in article.words:
                    print("match")

            yield item


class GoogleRssSpider(scrapy.spiders.XMLFeedSpider):
    name = 'google_rss'
    allow_domains = ['google.com']
    start_urls = ['https://news.google.com/news/feeds?ned=us&topic=w&output=rss']
    itertag = 'item'

    def parse_node(self, response, node):
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url.strip(), callback=self.parse_news)

    def parse_news(self, response):
        item = MediaArticle()
        # only log the warning info from request
        logging.getLogger("requests").setLevel(logging.WARNING)

        for href in response.xpath('//h2[@class="title"]/a/@href').extract():
            # use newspaper-0.0.8 to scrape the webpage, then get clean text.
            article = Article(item['link'])
            article.download()
            article.parse()
            article.nlp()

            item['link'] = href
            item['title'] = article.title
            item['summary'] = article.summary
            item['text'] = article.text
            # item['authors'] = article.authors
            # item['date'] = article.publish_date
            item['domain'] = response.meta['topic']
            for businessName in open("static_names.csv").readlines():
                if businessName in article.words:
                    print("match")

            yield item
