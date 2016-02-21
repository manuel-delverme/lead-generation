from scrapy.conf import settings
from scrapy.downloadermiddlewares.retry import RetryMiddleware

class RetryChangeProxyMiddleware(RetryMiddleware):
    def _retry(self, request, reason, spider):
        if "captcha" in request.url:
            log.msg('captcha redirect; Changing proxy')
            tn = telnetlib.Telnet('127.0.0.1', 9051)
            tn.read_until("Escape character is '^]'.", 2)
            # tn.write('AUTHENTICATE "267765"\r\n')
            # tn.read_until("250 OK", 2)
            tn.write("signal NEWNYM\r\n")
            tn.read_until("250 OK", 2)
            tn.write("quit\r\n")
            tn.close()
            time.sleep(3)
            log.msg('Proxy changed')
        return RetryMiddleware._retry(self, request, reason, spider)

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')
