from nltk.stem.porter import PorterStemmer
import string
import nltk
import sys
import json
import shelve
import collections
import RAKE

FREQFILE = "enwiki-20150602-words-frequency.txt"

class baseClassifier(object):
    def __init__(self):
        global FREQFILE
        self.wordfreqs = shelve.open("/tmp/wordfreq", flag="c")
        if '__filename__' not in self.wordfreqs or self.wordfreqs['__filename__'] != FREQFILE:
            self.wordfreqs.close()
            self.wordfreqs = shelve.open("/tmp/wordfreq", flag="n")

        self.stemmer = PorterStemmer()
        self.stopwords = set(nltk.corpus.stopwords.words('italian'))
        self.stopwords.union(nltk.corpus.stopwords.words('english'))

        with open(FREQFILE) as f:
            for wordfreq in f:
                key, freq = wordfreq[:-1].split()
                if(is_unicode(key)):
                    break
                freq = float(freq)
                key = str(self.stemmer.stem(key))
                try:
                    self.wordfreqs[key] += freq
                except KeyError:
                    self.wordfreqs[key] = freq


    def extract_keywords(self, text):
        if ''  == text:
            return collections.OrderedDict([])
        words = self.transform(text)
        fdist = nltk.FreqDist(words)
        result = dict()
        for word in words:
            if word in self.wordfreqs:
                result[word] = fdist[word] / self.wordfreqs[word]

        # normalize
        if len(result) > 0:
            max_val = max(result.values())

        for word in fdist:
            if word not in result:
                result[word] = 1.1
            else:
                result[word] /= max_val

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
    print "loaded"
    c = baseClassifier()
    with open(sys.argv[1]) as f:
        for row in f:
            row = json.loads(row)
            classification = row['dmoz_url'].split("/")[5:]
            text = " ".join(row['metadata'])
            if(is_unicode(text)):
                continue
            text = text.decode('utf8')
            for keyword in Rake.run(text):
                print keyword
            print "target:", classification
            for keyword,value in c.extract_keywords(text).items():
                print keyword, value
            print text, "$"

            raw_input()
