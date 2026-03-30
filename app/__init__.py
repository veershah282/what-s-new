from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv() # Load variables from .env

app = Flask(__name__)
from .config import Config
app.config.from_object(Config)

from app import views