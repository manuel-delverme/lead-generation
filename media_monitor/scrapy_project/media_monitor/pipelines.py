# -*- coding: utf-8 -*-
import newspaper
import json
import helper
from newspaper import Article
from media_monitor.items import MediaArticle
import errno
import os
import pickle
from scrapy.utils.serialize import ScrapyJSONEncoder


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class ArticleParsePipeline(object):
    def process_item(self, item, spider):
        article = Article('')
        article.set_html(item['text'])
        article.parse()

        item['title'] = article.title
        item['text'] = article.text
        item['authors'] = article.authors
        item['date'] = article.publish_date
        return item

class CacheBagOfWordsPipeline(object):
    def persist_to_db(self, word_set, uri):
        pass

    def process_item(self, item, spider):
        word_set = set(newspaper.nlp.split_words(item['text']))
        self.persist_to_db(word_set, item['url'])
        return item

class StoreArticlePipeline(object):

    def process_item(self, item, spider):
        base_path = helper.get_news_file_url(item['url'])
        text_path = base_path + "/text"
	mkdir_p(base_path)

        with open(text_path, "w") as f:
            f.write(item['text'].encode('utf-8'))
            del item['text']

        _encoder = ScrapyJSONEncoder()
        metadata_path = base_path + "/metadata"
        with open(metadata_path, "w") as f:
            json.dump(_encoder.encode(item), f)
        return item
