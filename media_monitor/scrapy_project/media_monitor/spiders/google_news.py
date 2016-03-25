import scrapy
import scrapy.spiders
from media_monitor.items import MediaArticle
import newspaper.nlp
import logging
from newspaper import Article


class GoogleRssSpider(scrapy.spiders.XMLFeedSpider):
    name = 'google_rss'
    allow_domains = ['google.com']
    itertag = 'item'

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
            url = "https://news.google.it/news/feeds?cf=all&pz=1&ned=it&output=rss&topic={}".format(topic)
            yield scrapy.Request(url, self.parse, meta={'topic': topic})
            # TODO add pages or similar

    def parse_node(self, response, node):
        for full_url in node.xpath('link/text()').extract():
            yield scrapy.Request(full_url, self.parse_news, meta=response.meta)

    def parse_news(self, response):
        item = MediaArticle()
        # only log the warning info from request
        logging.getLogger("requests").setLevel(logging.WARNING)

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
                # yield item
