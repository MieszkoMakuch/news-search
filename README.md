# News search

News search engine with fake news detection implemented in Python using micro web framework Flask.

## Online demo

### https://search-news.herokuapp.com/

**Note:** it may take a few seconds to deploy

## Functionality
- **Web crawling:** app can download and validate all articles from the given domains
- **Article indexing:** bag-of-words, inverse document frequency, SVD and low rank approximation
- **Fake news detection:** articles are classified using my [Fake news detector](https://github.com/MieszkoMakuch/fakenews-detector) python package

## Preview


### Search results:
![](https://raw.githubusercontent.com/MieszkoMakuch/news-search/master/readme-files/search-results.png)

### Example fake news analysis:
![](https://raw.githubusercontent.com/MieszkoMakuch/news-search/master/readme-files/real-news.png)

### Example fake news analysis:
![](https://raw.githubusercontent.com/MieszkoMakuch/news-search/master/readme-files/watch-out.png)

## Technologies used
Frontend:
- Bootstrap
- JS, jQuery

Backend:
- Python
- Flask
- Template engine: Jinja