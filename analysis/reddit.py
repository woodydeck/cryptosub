#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gathering reddit posts"""

from logger import log
import csv
import sys
import os
import datetime
from pathlib import Path
from prawcore.exceptions import PrawcoreException
import praw
import json
import pandas as pd
from configparser import ConfigParser
from pymongo import MongoClient

parser = ConfigParser()
parser.read('config.conf')


# Connect to DB
client = MongoClient(parser.get('db', 'url'))
db = client.dev



def Stream(subs):
    
    # init Reddit instance
    reddit = praw.Reddit(
        client_id=parser.get('reddit', 'client_id'), 
        client_secret=parser.get('reddit', 'client_secret'), 
        password=parser.get('reddit', 'password'), 
        user_agent=parser.get('reddit', 'user_agent'), 
        username=parser.get('reddit', 'username'))


    CommentCounter = 0
    PostCounter = 0

    while True:
        try:
            # Get subreddits
            subreddits = reddit.subreddit(subs)
            # Stream comments recieved to subreddits
            for comment in subreddits.stream.comments():
                # Get post
                submission = comment.submission
                # commentcounter++
                CommentCounter += 1
                # add the comment to the appropriate csv file
                SaveComments(str(submission.subreddit), [comment.id, comment.id, comment.body, comment.created_utc, comment.score, comment.author])
                # Log details
                Logger(submission.subreddit,submission.created_utc, CommentCounter, PostCounter)
                # Get postIDs
                PostIDs = getPostIDs()
                # Check if already processed
                if submission.id in PostIDs:
                    continue
                # Add current postID to data frame and save back to csv
                updatePostIDs(submission.id)
                # Save post to appropriate csv file
                SavePosts(str(submission.subreddit), [submission.id, submission.title, submission.created_utc, submission.score, submission.num_comments, submission.author])
                PostCounter += 1
                Logger(submission.subreddit,submission.created_utc,CommentCounter,PostCounter)

        except KeyboardInterrupt:
            log('Termination received. Goodbye!')
            return False
        except PrawcoreException:
            log(PrawcoreException, newline=True)

def getPostIDs():
    PostIDs = db.misc.find({},{"PostIDs": 1})
    return PostIDs[0]["PostIDs"]

def updatePostIDs(PostID):
    db.misc.update_one({},{'$push': {'PostIDs': PostID}})

def getSubreddits():
    Subreddits = db.misc.find({},{"subs": 1})
    return Subreddits[0]["subs"]

#Display mining information to the terminal
def Logger(sub,date,CommentCounter,PostCounter):
    date = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    log("({0}) Posts:{1} - Comments:{2} - Last:{3}".format(sub,PostCounter,CommentCounter,date), returnline=True)

    

def SavePosts(subreddit, posts):
    path = parser.get('path', 'LatestDirectory') + '/posts_'+subreddit+'.csv'
    posts_file = Path(path)
    file_exists = posts_file.is_file()        
    f = open(path, 'a')
    try:
        writer = csv.writer(f)        
        if file_exists is False:
            writer.writerow(["ID", "Text", "Date", "Score", "No. Comments", "Author"])
        writer.writerow(posts)
    finally:
        f.close()
        
def SaveComments(subreddit, comments):
    path = parser.get('path', 'LatestDirectory') + 'comments_'+subreddit+'.csv'    
    comments_file = Path(path)
    file_exists = comments_file.is_file() 
    f = open(path, 'a')
    try:
        writer = csv.writer(f)
        if file_exists is False:
            writer.writerow(["ID", "PostID", "Text", "Date", "Score", "Author"])
        writer.writerow(comments)
    finally:
        f.close()


if __name__ == '__main__':
    # Load subreddit list
    subreddits = pd.DataFrame.from_records(data=getSubreddits())
    subs = []
    for i, row in subreddits.iterrows():
        subs.append(row["Subreddit"])
    subs = '+'.join(subs)
    Stream(subs)
    