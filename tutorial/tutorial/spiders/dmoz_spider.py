import scrapy
import urlparse

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
    ]

    def parse(self, response):
        """
            1) gather all the links
            2) drop relative links
            3) remove paths from absolute links
        """
        request_url = urlparse.urlparse(response.url)
        for href in response.css("a::attr('href')"):
            url = urlparse.urlparse(href.extract())
            if url.netloc == request_url.netloc or url.netloc == "":
                # it's relative
                continue
            url = url._replace(path='', query='', fragment='')
            yield scrapy.Request(url, callback=self.parse_metaddata)

    def parse_metaddata(self, response):
        item = DmozItem()
        for metafield in response.selector.xpath("//meta"):
            #metavalue = metafield.xpath([@name='description']/@content"))
            item['metadata'] = metafield.extract()
            yield item
