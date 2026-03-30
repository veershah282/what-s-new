import os
import sqlite3
from flask import g

DATABASE = os.path.join('/tmp', 'news_hub.db') if os.environ.get('VERCEL') else 'news_hub.db'
DB_URL = os.environ.get("TURSO_DATABASE_URL")
DB_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if DB_URL:
            # Use Turso (libsql-client)
            try:
                import libsql_client
                db = g._database = libsql_client.create_client_sync(DB_URL, auth_token=DB_TOKEN)
            except ImportError:
                # Fallback to local if client not installed or failing
                db = g._database = sqlite3.connect(DATABASE)
                db.row_factory = sqlite3.Row
        else:
            # Use local SQLite
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row
    return db

def init_db(app):
    with app.app_context():
        db = get_db()
        query = '''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT,
                description TEXT,
                image_url TEXT,
                published_at TEXT
            )
        '''
        if DB_URL:
            db.execute(query)
        else:
            with db:
                db.execute(query)

def add_bookmark(title, url, source, description, image_url, published_at):
    db = get_db()
    query = '''
        INSERT INTO bookmarks (title, url, source, description, image_url, published_at)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    params = (title, url, source, description, image_url, published_at)
    
    try:
        if DB_URL:
            db.execute(query, params)
        else:
            with db:
                db.execute(query, params)
        return True
    except Exception as e:
        # Check specifically for integrity error (URL is UNIQUE)
        if "UNIQUE constraint failed" in str(e) or "already exists" in str(e).lower():
            return False
        raise e

def get_bookmarks():
    db = get_db()
    query = 'SELECT * FROM bookmarks ORDER BY id DESC'
    if DB_URL:
        # libsql client's execute returns a ResultSet, where .rows is the list of rows
        result = db.execute(query)
        return result.rows
    else:
        cursor = db.execute(query)
        return cursor.fetchall()

def remove_bookmark(url):
    db = get_db()
    query = 'DELETE FROM bookmarks WHERE url = ?'
    params = (url,)
    if DB_URL:
        db.execute(query, params)
    else:
        with db:
            db.execute(query, params)
