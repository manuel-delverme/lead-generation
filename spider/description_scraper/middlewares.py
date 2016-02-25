# modify  scrapy behavoir

from scrapy.conf import settings
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware, MetaRefreshMiddleware
import scrapy.utils.response
import logging
import telnetlib
import time

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
        import ipdb;ipdb.set_trace()
        if hasattr(spider, 'cookies') and hasattr(spider, 'headers'):
            request = request.replace(cookies=spider.cookies, headers=spider.headers)
            return request

#class ProxyMiddleware(object):
#    def process_request(self, request, spider):
#        request.meta['proxy'] = settings.get('HTTP_PROXY')
