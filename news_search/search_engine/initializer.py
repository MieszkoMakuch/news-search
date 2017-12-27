import codecs
import os
import threading

import newspaper
from fakenews_detector.url_utils import get_domain, format_url


class Initializer:
    module_dir = os.path.dirname(__file__)
    articles_dir = module_dir + '/resources/articles'
    matrix_dir = module_dir + '/resources/data2_downloaded.dat'

    @staticmethod
    def get_articles_from_domain(domain):
        domain = format_url(domain)
        print(domain)
        site_with_articles = newspaper.build(domain, memoize_articles=False)
        site_with_articles.print_summary()

        domain_directory_name = get_domain(format_url(domain)).replace('.', '_')
        download_directory = Initializer.articles_dir + '/' + domain_directory_name
        Initializer.mkdir_if_not_exist(download_directory)

        saved_article_counter = 0
        for article in site_with_articles.articles:
            print('article : ' + article.url)

            # download and parse article
            article.config.MIN_WORD_COUNT = 100  # num of word tokens in text
            article.config.MIN_SENT_COUNT = 3  # num of sentence tokens
            article.config.MAX_TITLE = 200  # num of chars
            article.config.MAX_TEXT = 1000000  # num of chars
            article.config.MAX_KEYWORDS = 70  # num of strings in list
            article.config.MAX_AUTHORS = 20  # num strings in list
            article.config.MAX_SUMMARY = 50000  # num of chars
            article.config.MAX_SUMMARY_SENT = 50  # num of sentences
            article.download()
            if not article.is_downloaded:
                print('Could not download: article : ' + article.url)
                continue
            article.parse()
            if article.is_valid_body():
                article.nlp()
                saved_article_counter += 1
                Initializer.save_valid_article_as_json(article=article, counter=saved_article_counter,
                                                       directory=download_directory)
            else:
                print('Not a valid article: article : ' + article.url)

    @staticmethod
    def save_valid_article_as_json(article, counter, directory):
        data_to_save = {
            'article_id': article.link_hash,
            'title': article.title,
            'authors': article.authors,
            'canonical_link': article.canonical_link,
            'url': article.url,
            'top_img': article.top_img,
            'meta_img': article.meta_img,
            # 'imgs': article.images, #AttributeError: 'Article' object has no attribute 'images'
            'movies': article.movies,
            'text': article.text,
            'keywords': article.keywords,
            'meta_keywords': article.meta_keywords,
            'publish_date': article.publish_date,
            'summary': article.summary,
            'article_html': article.article_html,
            'meta_description': article.meta_description,
            'meta_lang': article.meta_lang,
        }
        # print(data_to_save)
        import json
        from bson import json_util
        with open(Initializer.get_article_file_name(article, directory, counter),
                  'w') as outfile:
            json.dump(data_to_save, outfile, default=json_util.default, indent=4)

    @staticmethod
    def get_article_file_name(article, directory, counter):
        return directory + '/' + '{:05d}'.format(counter) + ' Title=' + article.title + '.json'

    @staticmethod
    def mkdir_if_not_exist(articles_dir):
        if not os.path.exists(articles_dir):
            os.makedirs(articles_dir)


def crawl():
    Initializer.mkdir_if_not_exist(Initializer.articles_dir)
    domains = [
        # reliable news
        'http://cnn.com/', 'bbc.com', 'wsj.com', 'washingtonpost.com', 'independent.co.uk', 'chicagotribune.com',
        'bostonglobe.com', 'nature.com', 'nytimes.com',
        # fake news
        'https://www.ancient-code.com/', 'http://creambmp.com/', 'http://crimeresearch.org/']
    for domain in domains:
        t = threading.Thread(target=Initializer.get_articles_from_domain, args=(domain,))
        t.start()

# crawl()
# solver.solve(Initializer.articles_dir, Initializer.matrix_dir)
