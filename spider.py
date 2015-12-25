import scrapy
import keywords

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['http://blog.scrapinghub.com']

    def parse(self, response):
        for url in response.css('ul li a::attr("href")').re(r'.*/\d\d\d\d/\d\d/$'):
            yield scrapy.Request(response.urljoin(url), self.parse_titles)

    def parse_titles(self, response):
        for post_title in response.css('div.entries > ul > li a::text').extract():
            yield {'title': post_title}


description = """It's no secret that car dealers have been struggling 
        to sell electric vehicles,... Dec 23, 2015. Nissan Pathfinder.
        Nissan Reveals Updates and Pricing on the 2016 """

keywords = keywords.extract_keywords(description)
for key,val in keywords.items():
    print val, key
