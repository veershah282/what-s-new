from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv() # Load variables from .env

app = Flask(__name__)
from .config import Config
app.config.from_object(Config)

from .database import init_db
try:
    init_db(app)
except Exception as e:
    print(f"Error initializing database: {e}")

from app import views