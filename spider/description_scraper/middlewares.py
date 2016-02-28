# modify  scrapy behavoir

from scrapy.conf import settings
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware, MetaRefreshMiddleware
from extruct.w3cmicrodata import MicrodataExtractor
import scrapy.utils.response
import logging
import telnetlib
import time
import requests

def change_tor_ip():
    logging.log(logging.INFO, 'captcha redirect; Changing proxy')
    tn = telnetlib.Telnet('127.0.0.1', 9051)
    tn.read_until("Escape character is '^]'.", 2)
    tn.write('AUTHENTICATE "{}"\r\n'.format(settings.get('TOR_PASSWORD')))
    tn.read_until("250 OK", 2)
    tn.write("signal NEWNYM\r\n")
    tn.read_until("250 OK", 2)
    tn.write("quit\r\n")
    tn.close()
    time.sleep(3)
    logging.log(logging.INFO, 'Proxy changed')

class InterceptRedirectMiddleware(RedirectMiddleware):
    def process_response(self, request, response, spider):
        if "captcha" in response.url:
            import ipdb;ipdb.set_trace()
            #TODO this part is not tested
            change_tor_ip()
            redirected = request.replace(url=request.referrer)
            return self._redirect(redirected, request, spider, "captcha")

        # TODO fallback to old middleware
        return response

class InterceptMetaRefreshMiddleware(MetaRefreshMiddleware):
    def process_response(self, request, response, spider):
        try:
            _, refresh_url = scrapy.utils.response.get_meta_refresh(response)
        except AttributeError as e:
            if e.message == "'Response' object has no attribute 'body_as_unicode'":
                return response
        else:
            if refresh_url is not None and "captcha" in refresh_url:
                import ipdb;ipdb.set_trace()
                change_tor_ip()
                return self._redirect(request, request, spider, "captcha")

        # TODO fallback to old middleware
        return response

class InterceptDownloadMiddleware(object):
    def process_request(self, request, spider):
        if "www.paginegialle.it" in request.url and "sitemap" not in request.url:
            cookies = { 'kpi': '487ac7e9.52bd6ba6757e9', 'pgz': 'ODQ1ODg7VG9yaW5vO1RPOzkx', 's_fid': '3B28DCB04B474A02-32409839669463F5', 's_lv': '1456613168944', 's_nr': '1456613168945-Repeat', 'D_SID': '93.32.198.27:lZDI2wmzmKocezaETE9JzbKK+jviQOnwVQ7RCsiNcKk', 'D_PID': '3119DF0B-3C06-308A-88B4-6118E4B86D16', 'D_IID': 'ADC1D2B9-30C0-3662-A527-E3EA44049139', 'D_UID': 'AE658B91-6CC1-3DB4-9125-507D4FFE2986', 'D_HID': 'juKea4kmyk/9PbJpQ1nlghHp3WMWx/deqp/EaUzj0bg', '__rtgxg': '105DE608-C036-0001-BCA8-1DD014CE19D0', '__rtgxh': '1455576136114$1455576136114$1', '_ga': 'GA1.2.910544111.1455576136', 'cp_acc': '1', 'sessionid': '3456817416558958244', 's_cc': 'true', 's_lv_s': 'More%20than%207%20days', 'gpv_p24': 'PGIT%3AScheda%3AClient%3AHpsche', 's_sq': '%5B%5BB%5D%5D', '_gat': '1', }
            headers = { 'Host': 'www.paginegialle.it', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', }

            import ipdb;ipdb.set_trace()

            _response = requests.get(request.url, headers=headers, cookies=cookies)
            response = scrapy.http.HtmlResponse(url=_response.url,status=_response.status_code,headers=_response.headers.iteritems(),body=_response.text,encoding="utf-8")

            extractor = MicrodataExtractor()
            items = extractor.extract(response.body_as_unicode(), response.url)['items']
            descriptions = response.xpath("//meta[@name='description']/@content").extract() + response.xpath("//meta[@property='og:description']/@content").extract()
            homepage_url = response.css(".website").extract()
            homepage_request = scrapy.Request(cookies=self.cookies, callback=self.parse_homepage)
            
            homepage_request.meta['dt_pg_description'] = descriptions
            homepage_request.meta['dt_pg_keywords'] = response.xpath("//meta[@name='keywords']/@content").extract()
            homepage_request.meta['dt_pg_title'] = response.xpath("//meta[@property='og:title']/@content").extract()
            homepage_request.meta['dt_microdata'] = items
            homepage_request.meta['dt_referrer'] =  response.url
            return homepage_request

#class ProxyMiddleware(object):
#    def process_request(self, request, spider):
#        request.meta['proxy'] = settings.get('HTTP_PROXY')
