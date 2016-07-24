import urlparse
def get_news_file_url(news_url):
    _, netloc, path, query, _ = urlparse.urlsplit(news_url)
    base_path = "/news/{}/{}/{}".format(netloc, path.replace("/", "|")[1:], query)

    if base_path.endswith("/"):
        base_path = base_path.rstrip("/")
    if len(base_path) > 230:
        base_path = base_path[:230]
    return base_path
