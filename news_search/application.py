import logging
import sys
import threading

from flask import Flask, request, render_template, redirect, url_for

from news_search.fakenews_detector import analyze_article
from news_search.config import Config, initialize_application_config, prevent_herokuapp_from_sleeping
from news_search.search_engine import search_engine

app = Flask(__name__)

# Defaults to stdout
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
try:
    log.info('Logging to console')
except:
    _, ex, _ = sys.exc_info()
    log.error(ex.message)

t = threading.Thread(target=prevent_herokuapp_from_sleeping, args=())
# t.start()


@app.route('/')
def index():
    print('in def index():')
    if not Config.was_initialized:
        initialize_application_config()
    return render_template('index.html')


@app.route('/articles/show')
def show_article():
    url_to_clean = request.args.get('url_to_clean')
    if not url_to_clean:
        return redirect(url_for('index'))

    # Fake news
    article = analyze_article(url_to_clean, log)
    return render_template('article/index.html', article=article, url=url_to_clean)


@app.route('/search')
def search():
    query = request.args.get('query')
    search_results = search_engine.search(query=query)
    if not search_results:
        return no_results_template(query)
    return render_template('search_results.html', search_results=search_results, query=query)


@app.route('/search/lucky')
def search_lucky():
    query = request.args.get('query')
    search_results = search_engine.search(query=query)
    if not search_results:
        return no_results_template(query)
    return redirect(search_results[0][1]['canonical_link'])


def no_results_template(query):
    return render_template('simple_message.html', title='No results found',
                           message='Your search - <b>' + query + '</b> - did not match any documents.'
                                                                 '<br>Suggestions:<br><ul>'
                                                                 '<li>Make sure that all words are spelled correctly.</li>'
                                                                 '<li>Try different keywords.</li>'
                                                                 '<li>Try more general keywords.</li>'
                                                                 '<li>Try fewer keywords.</ul>')


@app.route('/reset_config')
def reset_config():
    initialize_application_config()
    return render_template('simple_message.html', title='Application config updated', message='Config attributes: <br>' + str(vars(Config)))
