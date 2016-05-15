from scrapy.dupefilters import RFPDupeFilter
import os
import helper

class NewsRFPDupeFilter(RFPDupeFilter):
    """
        dupefilters based on news storage
        look into pybloom if speedup required
    """

    def request_seen(self, request):
        uri = helper.get_news_file_url(request.url)
        if os.path.exists(uri):
            return True
        return False
