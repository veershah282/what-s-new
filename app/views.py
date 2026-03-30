from app import app
from flask import render_template
from .request import businessArticles, entArticles, get_news_source, healthArticles, publishedArticles, randomArticles, scienceArticles, sportArticles, techArticles, topHeadlines, searchArticles
from datetime import datetime
from flask import request, redirect, url_for, flash
from .database import add_bookmark, get_bookmarks, remove_bookmark
from textblob import TextBlob
import math

# init_db(app) is now called in app/__init__.py

def format_articles_for_strip(articles_list):
    strip_items = []
    now = datetime.utcnow()

    for source, title, desc, author, img, p_date, url in articles_list:
        # 10-word headline
        title_words = title.split()
        short_title = " ".join(title_words[:10])
        if len(title_words) > 10:
            short_title += "..."

        # 60-word summary
        desc_text = desc if desc else ""
        desc_words = desc_text.split()
        summary = " ".join(desc_words[:60])
        if len(desc_words) > 60:
            summary += "..."

        # Time ago
        try:
            # NewsAPI date format: 2026-03-30T00:03:49Z
            published_at = datetime.strptime(p_date, '%Y-%m-%dT%H:%M:%SZ')
            diff = now - published_at
            
            if diff.days > 0:
                time_ago = f"{diff.days}d ago"
            elif diff.seconds // 3600 > 0:
                time_ago = f"{diff.seconds // 3600}h ago"
            elif diff.seconds // 60 > 0:
                time_ago = f"{diff.seconds // 60}m ago"
            else:
                time_ago = "just now"
        except:
            time_ago = p_date

        strip_items.append({
            'title': short_title,
            'summary': summary,
            'source': source['name'] if isinstance(source, dict) else str(source),
            'time_ago': time_ago,
            'url': url,
            'image_url': img,
            'p_date': p_date,
            'desc': desc
        })
    return strip_items

@app.route('/')
def home():
    articles_list = publishedArticles()
    headlines_list = topHeadlines()
    strip_items = format_articles_for_strip(headlines_list)

    return render_template('home.html', articles=articles_list, strip_items=strip_items)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('home'))
    
    articles_list = searchArticles(query)
    strip_items = format_articles_for_strip(articles_list)
    
    return render_template('search.html', articles=articles_list, strip_items=strip_items, query=query)

@app.route('/bookmark/add', methods=['POST'])
def add_to_bookmarks():
    title = request.form.get('title')
    url = request.form.get('url')
    source = request.form.get('source')
    desc = request.form.get('desc')
    img = request.form.get('img')
    date = request.form.get('date')
    
    if add_bookmark(title, url, source, desc, img, date):
        flash('Article bookmarked!', 'success')
    else:
        flash('Article already bookmarked!', 'info')
        
    return redirect(request.referrer or url_for('home'))

@app.route('/bookmarks')
def bookmarks():
    saved = get_bookmarks()
    return render_template('bookmarks.html', bookmarks=saved)

@app.route('/bookmark/remove', methods=['POST'])
def remove_from_bookmarks():
    url = request.form.get('url')
    remove_bookmark(url)
    flash('Bookmark removed.', 'success')
    return redirect(url_for('bookmarks'))

@app.route('/headlines')
def headlines():
    return redirect(url_for('home'))

@app.route('/articles')
def articles():
    return redirect(url_for('home'))

@app.route('/sources')
def sources():
    newsSource = get_news_source()
    return render_template('sources.html', newsSource = newsSource)

@app.route('/category/business')
def business():
    sources = businessArticles()
    return render_template('business.html', sources = sources)

@app.route('/category/tech')
def tech():
    sources = techArticles()
    return render_template('tech.html', sources = sources)

@app.route('/category/entertainment')
def entertainment():
    sources = entArticles()
    return render_template('entertainment.html', sources = sources)

@app.route('/category/science')
def science():
    sources = scienceArticles()
    return render_template('science.html', sources = sources)

@app.route('/category/sports')
def sports():
    sources = sportArticles()
    return render_template('sport.html', sources = sources)

@app.route('/category/health')
def health():
    sources = healthArticles()
    return render_template('health.html', sources = sources)

@app.route('/analysis')
def analysis():
    categories = ['Business', 'Tech', 'Entertainment', 'Science', 'Sports', 'Health']
    category_funcs = [businessArticles, techArticles, entArticles, scienceArticles, sportArticles, healthArticles]
    
    category_sentiment = {}
    total_sentiment = 0
    count = 0
    
    for cat, func in zip(categories, category_funcs):
        articles = func()
        cat_total = 0
        cat_count = 0
        
        for art in articles:
            title = art[1]
            sentiment = TextBlob(title).sentiment.polarity
            total_sentiment += sentiment
            cat_total += sentiment
            cat_count += 1
            count += 1
            
        if cat_count > 0:
            category_sentiment[cat] = round(cat_total / cat_count, 2)
        else:
            category_sentiment[cat] = 0
            
    avg_sentiment = total_sentiment / count if count > 0 else 0
    
    if avg_sentiment > 0.05:
        mood, mood_color = "Positive", "#28a745"
    elif avg_sentiment < -0.05:
        mood, mood_color = "Negative", "#007bff"
    else:
        mood, mood_color = "Neutral", "#ffc107"
        
    return render_template('analysis.html', 
                           avg_sentiment=round(avg_sentiment, 2),
                           mood=mood,
                           mood_color=mood_color,
                           category_sentiment=category_sentiment)