from xml.etree import ElementTree

from fakenews_detector.main import check_news
from fakenews_detector.news_info import NewsVerdict, AIInfo


def verdict_to_str(verdicts):
    main_verdict = verdicts[0]
    verdict_str = 'Unknown'
    bg_color = '#03A9F4'
    icon = 'glyphicon-question-sign'
    if main_verdict == NewsVerdict.FAKE:
        verdict_str = 'Fake news'
        bg_color = '#F44336'
        icon = 'glyphicon-exclamation-sign'
    elif main_verdict == NewsVerdict.REAL:
        verdict_str = 'Real news'
        bg_color = '#6cc76c'
        icon = 'glyphicon-ok'
    elif main_verdict == NewsVerdict.WARNING:
        verdict_str = 'Watch out!'
        bg_color = '#ffa500'
        icon = 'glyphicon-warning-sign'
    return verdict_str, bg_color, icon


def source_notes_to_str(source_notes):
    if len(source_notes) > 2:
        return source_notes[2]
    else:
        return '-'


def analyze_article(url, log):
    try:
        analysis_list = check_news(url)
    except Exception as err:
        article_analyse = {
            'verdict': 'Cannot perform analysis',
            'description': str(err),
            'bgcolor': '#03A9F4',
            'icon': 'glyphicon-question-sign'
        }
        return article_analyse

    if len(analysis_list) == 0:
        article_analyse = {
            'verdict': 'Cannot perform analysis',
            'description': 'Make sure that provided url is valid.',
            'bgcolor': '#03A9F4',
            'icon': 'glyphicon-question-sign'
        }
        return article_analyse

    main_analyse = analysis_list[0]
    verdicts, categories, descriptions, source_notes = main_analyse

    verdict_str, bg_color, icon = verdict_to_str(verdicts)
    article_analyse = {
        'verdict': verdict_str,
        'source': source_notes[1],
        'source_notes': source_notes_to_str(source_notes),
        'description': descriptions[0],
        'bgcolor': bg_color,
        'icon': icon
    }
    can_download_article, article = AIInfo.can_check_url(url, None)
    if can_download_article:
        try:
            html_string = ElementTree.tostring(article.clean_top_node)
        except:
            html_string = "Error converting html to string."
        try:
            article.nlp()
        except:
            log.error("Couldn't process with NLP")
        article_analyse.update({
            'html': html_string,
            'authors': str(', '.join(article.authors)),
            'title': article.title,
            'text': article.text,
            'top_image': article.top_image,
            'keywords': str(', '.join(article.keywords)),
            'summary': article.summary
        })

    return article_analyse
