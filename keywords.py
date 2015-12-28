from nltk.stem.porter import PorterStemmer
import string
import nltk
import sys
import json
import shelve
import collections


class Classifier(object):
    def __init__(self):
        self.wordfreqs = shelve.open("/tmp/wordfreq")
        self.stemmer = PorterStemmer()
        with open("enwiki-20150602-words-frequency.txt") as f:
            for wordfreq in f:
                key, freq = wordfreq[:-1].split()
                key = self.stemmer.stem(key)
                try:
                    self.wordfreqs[key] += freq
                except KeyError:
                    self.wordfreqs[key] = freq

    def extract_keywords(self, text):
        words = self.transform(text)
        fdist = nltk.FreqDist(words)
        result = dict()
        for word in words:
            if word in self.wordfreqs:
                result[word] = fdist[word] / self.wordfreqs[word]

        # normalize
        max_val = max(result.values())
        for word in fdist:
            if word not in result:
                result[word] = 1.1
            else:
                result[word] /= max_val

        return collections.OrderedDict(sorted(result.items(), key=lambda k:-k[1]))

    def transform(text, stem=True):
        stopwords = set(nltk.corpus.stopwords.words('italian'))
        stopwords.union(nltk.corpus.stopwords.words('english'))

        tokens = nltk.word_tokenize(text)
        filtered_tokens = list()
        for token in tokens:
            if token not in string.punctuation and token not in stopwords:
                filtered_tokens.append(token.lower())

        if stem:
            stemmed = []
            for item in filtered_tokens:
                stemmed.append(self.stemmer.stem(item))
            return stemmed
        else:
            return filtered_tokens

if __name__ == '__main__':
    c = Classifier()
    with open(sys.argv[1]) as f:
        for row in f:
            row = json.loads(row)
            classification = row['dmoz_url'].split("/")[5:]
            text = " ".join(row['metadata'])
            print c.extract_keywords(row[:-1]), classification
