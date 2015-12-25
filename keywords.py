from nltk.stem.porter import PorterStemmer
import string
import nltk
import sys
import collections

def extract_keywords(text):
    words = transform(text)
    fdist = nltk.FreqDist(words)
    result = dict()
    with open("wikipedia-word-frequency/enwiki-20150602-words-frequency.txt") as f:
        for wordfreq in f:
            key, freq = wordfreq[:-1].split()
            if key in words:
                result[key] = fdist[key] / float(freq)

    max_val = max(result.values())
    for word in fdist:
        if word not in result:
            result[word] = 1
        else:
            result[word] /= max_val

    return collections.OrderedDict(sorted(result.items(), key=lambda k:-k[1]))

def transform(text, stem=False):
    stopwords = set(nltk.corpus.stopwords.words('italian'))
    stopwords.union(nltk.corpus.stopwords.words('english'))

    tokens = nltk.word_tokenize(text)
    filtered_tokens = list()
    for token in tokens:
        if token not in string.punctuation and token not in stopwords:
            filtered_tokens.append(token.lower())

    if stem:
        stemmer = PorterStemmer()
        stemmed = []
        for item in filtered_tokens:
            stemmed.append(stemmer.stem(item))
        return stemmed
    else:
        return filtered_tokens
