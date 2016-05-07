# -*- coding: utf-8 -*-
from media_monitor.items import MediaArticle

class ArticleParsePipeline(object):

    def process_item(self, item, spider):
        item = MediaArticle()

        article = Article(item.text, lang="it")
        # article.download(html=response.body)
        article.parse()

        item['link'] = article.url
        item['title'] = article.title
        item['text'] = article.text
        item['authors'] = article.authors
        item['date'] = article.publish_date
        yield item

class CacheBagOfWordsPipeline(object):
    def process_item(self, item, spider):
        word_set = set(newspaper.nlp.split_words(item['text'].text)))
        persist_to_db(word_set)

class StoreArticlePipeline(object):
    def process_item(self, item, spider):
        _, netloc, path, query, _ = urlparse.urlsplit(item['link'])
        base_path = "news/{}/{}/{}".format(netloc, path.replace("/", "|"), query)
        text_path = base_path + "/text"
        with open(text_path) as f:
            pickle.dump(item['text'], f)
            del item['text']

        metadata_path = base_path + "/metadata"
        with open(metadata_path) as f:
            pickle.dump(item, f)
