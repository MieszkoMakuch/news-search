import json
import os
import pickle

import nltk
import numpy as np
import scipy
from bson import json_util
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


class Indexer:
    def __init__(self):
        self.bag_of_words = []
        self.terms = []
        self.article_list = []
        self.terms_by_article = []

    def fill_terms(self, path):
        for root, dirs, files in os.walk(path):
            print('files: ' + ', '.join(files))
            for file in files:
                if file.endswith('.json'):
                    self.process_file(file, root)
            for directory in dirs:
                self.fill_terms(directory)
        self.terms = list(set(self.terms))  # to eliminate duplicates

    def process_file(self, file, root):
        print('Processing file: ' + file)
        fullpath = root + '/' + file
        article = self.load_article_from_file(fullpath)
        terms = self.get_terms(article['text'])
        self.article_list.append(article)
        self.terms_by_article.append(terms)
        self.terms += terms

    def fill_bags_of_words(self):
        number_of_terms = len(self.terms)
        for i in range(len(self.terms_by_article)):
            bag = [0] * number_of_terms
            for term in self.terms_by_article[i]:
                bag[self.terms.index(term)] += 1
            self.bag_of_words.append(bag)

    def inverse_document_frequency(self):
        docs, words = self.bag_of_words.shape
        for i in range(words):
            frequency_per_doc = self.bag_of_words[:, i]
            nw = 0
            for j in range(len(frequency_per_doc)):
                if frequency_per_doc[j] != 0:
                    nw += 1
            idf = np.log(docs / nw)
            self.bag_of_words[:, i] *= idf

    def singular_value_decomposition(self, k):
        u, s, v = np.linalg.svd(self.bag_of_words, full_matrices=False)
        a = np.zeros(self.bag_of_words.shape)
        for i in range(k):
            a += s[i] * np.outer(u.T[i], v[i])
        self.bag_of_words = a

    @staticmethod
    def get_terms(text):
        terms = nltk.word_tokenize(text)
        stop = stopwords.words('english')
        stemmer = SnowballStemmer('english')
        terms = [stemmer.stem(x) for x in terms if len(x) > 2 and x not in stop]
        return terms

    @staticmethod
    def load_article_from_file(path):
        data = json.load(open(path), object_hook=json_util.object_hook)
        return data


def index(articles_dir, matrix_path):
    indexer = Indexer()
    indexer.fill_terms(articles_dir)
    indexer.fill_bags_of_words()
    indexer.bag_of_words = np.array(indexer.bag_of_words).astype(float)
    indexer.inverse_document_frequency()

    data = {
        'matrix': scipy.sparse.csr_matrix(indexer.bag_of_words),
        'articles': indexer.article_list,
        'terms': indexer.terms
    }

    with open(matrix_path, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
