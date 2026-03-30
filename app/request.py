from .models import Articles
from .models import Sources
from newsapi import NewsApiClient
from .config import Config
import urllib.request,json,time
from threading import Lock

api_key=None
base_url=None
base_url_for_everything=None
base_url_top_headlines=None
base_source_list=None

# Caching logic
_cache = {}
_cache_lock = Lock()
CACHE_EXPIRY = 600 # 10 minutes

def get_cached_news(cache_key, fetch_func, *args, **kwargs):
    with _cache_lock:
        now = time.time()
        if cache_key in _cache:
            entry_time, data = _cache[cache_key]
            if now - entry_time < CACHE_EXPIRY:
                return data
        
        data = fetch_func(*args, **kwargs)
        _cache[cache_key] = (now, data)
        return data

# Singleton NewsAPI client
_newsapi_client = None
def get_newsapi_client():
    global _newsapi_client
    if _newsapi_client is None:
        _newsapi_client = NewsApiClient(api_key=Config.API_KEY)
    return _newsapi_client

def _fetch_articles_list(fetch_func, *args, **kwargs):
    get_articles = fetch_func(*args, **kwargs)
    all_articles = get_articles['articles']
    
    source, title, desc, author, img, p_date, url = [], [], [], [], [], [], []
    for article in all_articles:
        source.append(article['source'])
        title.append(article['title'])
        desc.append(article['description'] if article['description'] else "")
        author.append(article['author'] if article['author'] else "Unknown")
        img.append(article['urlToImage'] if article['urlToImage'] else "")
        p_date.append(article['publishedAt'])
        url.append(article['url'])
    
    return list(zip(source, title, desc, author, img, p_date, url))

def publishedArticles():
    def fetch():
        newsapi = get_newsapi_client()
        # Top 20 reliable English news sources
        sources = 'bbc-news,cnn,reuters,cnbc,the-verge,gizmodo,the-next-web,techradar,ars-technica,wired,bloomberg,business-insider,the-guardian-uk,the-wall-street-journal,the-washington-post,time,usa-today,abc-news,cbs-news,nbc-news'
        return _fetch_articles_list(newsapi.get_everything, sources=sources, language='en', sort_by='publishedAt')

    return get_cached_news('published_articles', fetch)

def topHeadlines():
    def fetch():
        newsapi = get_newsapi_client()
        sources = 'bbc-news,cnn,reuters,cnbc,the-verge,gizmodo,the-next-web,techradar,ars-technica,wired,bloomberg,business-insider,the-guardian-uk,the-wall-street-journal,the-washington-post,time,usa-today,abc-news,cbs-news,nbc-news'
        return _fetch_articles_list(newsapi.get_top_headlines, sources=sources)

    return get_cached_news('top_headlines', fetch)

def randomArticles():
    def fetch():
        newsapi = get_newsapi_client()
        sources = 'the-verge,gizmodo,the-next-web,wired,techradar,ars-technica'
        return _fetch_articles_list(newsapi.get_everything, sources=sources, language='en')

    return get_cached_news('random_articles', fetch)

def businessArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='business', language='en')

    return get_cached_news('business_articles', fetch)

def techArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='technology', language='en')

    return get_cached_news('tech_articles', fetch)

def entArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='entertainment', language='en')

    return get_cached_news('ent_articles', fetch)

def scienceArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='science', language='en')

    return get_cached_news('science_articles', fetch)

def sportArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='sports', language='en')

    return get_cached_news('sport_articles', fetch)

def healthArticles():
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_top_headlines, category='health', language='en')

    return get_cached_news('health_articles', fetch)

def searchArticles(query):
    def fetch():
        newsapi = get_newsapi_client()
        return _fetch_articles_list(newsapi.get_everything, q=query)

    return get_cached_news(f'search_{query}', fetch)

def get_news_source():
  '''
  Function that gets the json response to our url request
  '''
  get_news_source_url = 'https://newsapi.org/v2/sources?language=en&apiKey=' + Config.API_KEY
  with urllib.request.urlopen(get_news_source_url) as url:
    get_news_source_data = url.read()
    get_news_source_response = json.loads(get_news_source_data)

    news_source_results = None

    if get_news_source_response['sources']:
      news_source_results_list = get_news_source_response['sources']
      news_source_results = process_sources(news_source_results_list)

  return news_source_results

def process_sources(source_list):
  '''
  function that process the news articles and transform them to a list of objects
  '''
  news_source_result = []
  for news_source_item in source_list:
    name = news_source_item.get('name')
    description = news_source_item.get('description')
    url = news_source_item.get('url')

    if name:
      news_source_object = Sources(name, description,url)
      news_source_result.append(news_source_object)
  return news_source_result