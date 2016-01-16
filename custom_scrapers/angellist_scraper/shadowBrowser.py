from __future__ import print_function
import mechanize as m

class ShadowBrowser:
    """
        basic browser class which handles gets and posts
        the poit here is to minimize our signature to avoid detection
    """

    def __init__(self):
        self.isLoggedIn = None
        self.br = m.Browser()

        #br.set_all_readonly(False)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.set_handle_refresh(False)

        #TODO fetch random user agent here
        self.br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')]

    def open(self, url):
        return self.br.open(url, timeout=10)

    def get_response(self):
        return self.br.response()
