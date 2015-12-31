from nltk.stem.porter import PorterStemmer
import string
import nltk
import sys
import json
import shelve
import math
import collections
import RAKE

FREQFILE = "wikipedia-word-frequency/it-wiki-freq.txt"

class baseClassifier(object):
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

if __name__ == '__main__':
    Rake = RAKE.Rake("SmartStoplist.txt");
    c = baseClassifier()
    print "loaded"
    with open(sys.argv[1]) as f:
        for row in f:
            row = json.loads(row)
            classification = row['dmoz_url'].split("/")[5:]
            text = " ".join(row['metadata'])
            if(is_unicode(text)):
                continue
            text = text.decode('utf8')
            #for keyword in Rake.run(text):
            #    print keyword
            print "target:", classification
            for keyword,value in c.extract_keywords(text).items():
                print keyword, value
            for keyword in c.pos_tag(text):
                if keyword[0] not in c.stopwords:
                    if 'NN' == keyword[1]:
                        print keyword
            print text, "$"

            raw_input()
