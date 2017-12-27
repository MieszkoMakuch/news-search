import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer

from news_search.config import Config, initialize_application_config


def search(query):
    if not Config.was_initialized:
        initialize_application_config()
    indexed_articles = Config.indexed_articles

    scipy_sparse_matrix = indexed_articles['matrix']
    matrix = scipy_sparse_matrix.toarray()
    articles = indexed_articles["articles"]
    terms = indexed_articles["terms"]

    tokens = tokenize_query(query)
    number_of_terms = len(terms)
    bag = [0] * number_of_terms
    for term in tokens:
        if term in terms:
            bag[terms.index(term)] += 1
    bag = np.array(bag).astype(float)
    results = []
    article_count, words_count = matrix.shape
    for i in range(article_count):
        correlation_result = np.correlate(bag, matrix[i, :])
        results.append((correlation_result[0], articles[i]))
    results = sorted(results, key=lambda x: x[0], reverse=True)

    results = [(score, article) for (score, article) in results if score > 0]
    return remove_duplicated_articles(results)


def tokenize_query(query):
    tokens = nltk.word_tokenize(query)
    stammer = SnowballStemmer("english")
    tokens = [stammer.stem(x) for x in tokens]
    return tokens


def remove_duplicated_articles(results):
    # in some cases data matrix may contain duplicates
    # eg: http://independent.co.uk/news/...
    # and http://www.independent.co.uk/news/...
    results_without_duplicates = []
    article_urls = []
    for (score, article) in results:
        article_url = article['canonical_link']
        if article_url not in article_urls:
            results_without_duplicates.append((score, article))
            article_urls.append(article_url)
    return results_without_duplicates
