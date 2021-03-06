import sys
sys.path.append('../')

from cleanse import Cleanse
from mockdf import MockDF
from db import MongoDB as db
import pandas as pd
import os

from configparser import ConfigParser
parser = ConfigParser()
parser.read('../config.conf')

# Connect to DB
if os.environ['ENV'] == "test":
    url = "mongodb://mongo/"
else:
    url = parser.get('db', 'url')
db = db(url)

mock = MockDF()
dataframe = mock.getDataframe()

bannedusers = db.get_banned_users()
stopwords = pd.DataFrame.from_records(data=db.get_stopwords())

def test_cleanse():
    clean = Cleanse(dataframe, dataframe, stopwords, bannedusers)
    comments, posts = clean.get_data()
    assert isinstance(posts, pd.DataFrame)
    assert isinstance(comments, pd.DataFrame)
    assert len(posts.index) > 0
    assert len(comments.index) > 0
    assert "Author" in posts
    assert "Author" in comments
    assert "Text" in posts
    assert "Text" in comments
    assert "Date" in posts
    assert "Date" in comments
    assert "Score" in posts
    assert "Score" in comments

