# -*- coding: utf-8 -*-

# Scrapy settings for description_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'description_scraper'

SPIDER_MODULES = ['description_scraper.spiders']
NEWSPIDER_MODULE = 'description_scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS=1

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY=18

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN=1
CONCURRENT_REQUESTS_PER_IP=1

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False
#COOKIES_DEBUG=True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'description_scraper.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    #'description_scraper.middlewares.InterceptMetaRefreshMiddleware': 580,
    #'description_scraper.middlewares.InterceptRedirectMiddleware': 600,
    #'description_scraper.middlewares.InterceptDownloadMiddleware': 950,

    #'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    #'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'description_scraper.pipelines.DatabasePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
AUTOTHROTTLE_ENABLED=True
# The initial download delay
AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

DOWNLOAD_HANDLERS={'s3': None}
DUPEFILTER_DEBUG=True
TOR_PASSWORD="howdoicake?"
LOG_LEVEL="INFO"

DATABASE = {
    'drivername': 'postgres',
    'host': 'tuamadre.net',
    'port': '5432',
    'username': 'spider',
    'password': 'write_only',
    'database': 'grepr'
}
