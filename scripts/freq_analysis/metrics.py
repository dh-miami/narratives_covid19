import nltk
import nltk.util
from preprocess import preprocess
from collections import Counter

def ngrams(texts, n=1, ignore_stop_words=True):
    """
    list of strings where each string in the list is a tweet.
    returns a list of n-grams, where n is given.

    NOTE when n=1, this is just a word frequency query.
    """
    n_grams = []
    for text in texts:
        tokens, _, _ = preprocess(text)
        n_grams += nltk.ngrams(tokens, n)
    out = [(' '.join(value), count)
        for value, count in Counter(n_grams).most_common()]
    return out

def hashtags(texts):
    hashtags = []
    for text in texts:
        _, h, _ = preprocess(text)
        hashtags += h
    return Counter(hashtags).most_common()
