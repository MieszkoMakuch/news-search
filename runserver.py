from news_search.application import app

# update herokou: git push heroku master; heroku open
from news_search.config import Config, initialize_application_config

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5005)
