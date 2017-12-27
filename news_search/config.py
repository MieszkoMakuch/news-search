import json
import pickle
import sched
import sys
import time
import urllib

from news_search.search_engine.crawler import Initializer


class Config:
    was_initialized = False
    config_download_url = 'https://drive.google.com/uc?authuser=0&id=1VJmutrJ4lDeCjE9ybRPakQezveFpdmaG&export=download'
    indexed_articles_download_url = ''
    indexed_articles = {}
    herokuapp_url = 'https://search-news.herokuapp.com'
    is_prevention_form_sleep_enabled = False


def initialize_application_config():
    Config.was_initialized = True

    config_json = json.load(urllib.request.urlopen(Config.config_download_url))
    Config.indexed_articles_download_url = config_json['indexed_articles_url']

    print('Downloading indexed articles..')
    file = urllib.request.urlopen(Config.indexed_articles_download_url)
    Config.indexed_articles = pickle.load(file)
    print('Finished download: ' + Initializer.matrix_dir)


def prevent_herokuapp_from_sleeping():
    Config.is_prevention_form_sleep_enabled = True
    s = sched.scheduler(time.time, time.sleep)

    def make_request(sc):
        print('make request')
        try:
            urllib.request.urlopen(Config.herokuapp_url)
        except:
            _, ex, _ = sys.exc_info()
            print('Failed to ping heroku app: ' + Config.herokuapp_url + '. Reson: ' + str(ex))
        s.enter(ping_interval, 1, make_request, (sc,))

    ping_interval = 300  # 5 minutes
    s.enter(ping_interval, 1, make_request, (s,))
    s.run()
