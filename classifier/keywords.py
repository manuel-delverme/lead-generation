from nltk.stem.porter import PorterStemmer
from models import SearchEntry
import string
import nltk
import sys
import json
import shelve
import math
import collections
import RAKE
import models
import sqlalchemy

FREQFILE = "wikipedia-word-frequency/it-wiki-freq.txt"

class bagOfWordsClassifier(object):
    def __init__(self):
        global FREQFILE
        self.wordfreqs = shelve.open("/tmp/wordfreq", flag="c")
        self.stemmer = PorterStemmer()
        self.stopwords = set(nltk.corpus.stopwords.words('italian'))
        #self.stopwords.union(nltk.corpus.stopwords.words('english'))
        if '__filename__' not in self.wordfreqs or self.wordfreqs['__filename__'] != FREQFILE:
            self.wordfreqs.close()
            self.wordfreqs = shelve.open("/tmp/wordfreq", flag="n")


            with open(FREQFILE) as f:
                for wordfreq in f:
                    key, freq = wordfreq[:-1].split()
                    if(is_unicode(key)):
                        continue
                    freq = float(freq)
                    key = str(key)
                    #key = str(self.stemmer.stem(key))
                    try:
                        self.wordfreqs[key] += freq
                    except KeyError:
                        self.wordfreqs[key] = freq
            self.wordfreqs['__filename__'] = FREQFILE
            self.wordfreqs.sync()

    def extract_keywords(self, text):
        if ''  == text:
            return collections.OrderedDict([])
        words = self.transform(text)
        fdist = nltk.FreqDist(words)
        result = dict()
        for word in words:
            if word in self.wordfreqs:
                result[word] = fdist[word] / math.log(self.wordfreqs[word])

        # normalize
        #if len(result) > 0:
        #    max_val = max(result.values())

        #for word in result:
            #if word not in result:
            #    result[word] = 1.1
        #    result[word] /= max_val
        return collections.OrderedDict(sorted(result.items(), key=lambda k:-k[1]))

    def transform(self, text, stem=True):
        tokens = nltk.word_tokenize(text)
        filtered_tokens = list()
        for token in tokens:
            if token not in string.punctuation and token not in self.stopwords:
                filtered_tokens.append(token.lower())

        if stem:
            stemmed = []
            for item in filtered_tokens:
                stemmed.append(str(self.stemmer.stem(item)))
            return stemmed
        else:
            return filtered_tokens

    def pos_tag(self, text):
        tokens = nltk.word_tokenize(text)
        tagged_text = nltk.pos_tag(tokens)
        return tagged_text

def is_unicode(word):
    try:
        word.decode('ascii')
        return False
    except UnicodeDecodeError:
        return True
    except UnicodeEncodeError:
        return True

def process(Rake, bagc, data):
    bag_of_words = ".\n ".join(json.loads(data['meta_description']))
    meta_keywords = json.loads(data['meta_keywords'])

    if(is_unicode(bag_of_words)):
        return []
    bag_of_words = bag_of_words.decode('utf8')

    if len(meta_keywords) > 0:
        keywords = ",".join(json.loads(meta_keywords)).split(",")
    else:
        pos_tagged = bagc.pos_tag(bag_of_words)
        #for keyword,value in bagc.extract_keywords(bag_of_words).items():
        keywords = set([tag[0] for tag in pos_tagged if 'NN' in tag[1]])
    keywords = set([k.lower().strip() for k in keywords])
    return keywords

if __name__ == '__main__':

    #Rake = RAKE.Rake("SmartStoplist.txt");
    bagc = bagOfWordsClassifier()

    print "loaded"

    engine = models.db_connect()
    with sqlalchemy.orm.sessionmaker(engine=engine) as session:
        with engine.connect() as conn:
            for business in conn.execute('select * from "Businesses"'):
                target_result = business['referrer'].split("/")[5:]
                print "target:", target_result
                keywords = process(bagc, base_text, business)

                for keyword in keywords:
                    searchEntry = SearchEntry(business=business, keyword=keyword)
                    session.add(searchEntry)
                try:
                    session.commit()
                except:
                    session.rollback()
                    raise
            print base_text, "$"
            raw_input()
