#!/usr/bin/env python
# coding: utf-8

# In[162]:


import praw
import re
import os
import numpy as np
from Reddit_credentials import username, password, CLIENT_ID,CLIENT_SECRET
from collections import Counter
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

user_agent = "Scraper 1.0 by tnasc"
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=user_agent
)

# Global.. is this sinful?
logStart = datetime.now().strftime("%Y_%m_%d-%H:%M:%S")
start = datetime.now()

# relative paths from current working directory
base_path = '/Users/tiagonascimento/spiced_projects/Repository/garlic-boosting-student-code/tiago/Final Project'
logPath = str(base_path) + "/logs/" + "wsb_script_" + str(logStart) + ".log"


# In[4]:


def getThread():
    # set sub
    subreddit = reddit.subreddit("wallstreetbets")

    # thread logic: for sure would like the two pinned posts, possibly top 10 rising posts too?
    # for submission in subreddit.rising(limit=10):
    postList = []
    
    for submission in subreddit.hot(limit=3):
        # usually the top 2 `hot` submissions are stickied anyway, but an extra test to ensure
        if submission.stickied == True:
            postList.append(submission.id)
        

    # for dev/testing
    # postList = ['kjdkdk', 'kj17ga']
    # december 24 posts
    return postList
   # return getComments(postList,reddit)


# In[8]:


postList = getThread()
postList


# In[40]:


def getComments(postList):

      # allows all comments to be gathered, replacing "MoreComments" with a valid object
    
    # breadth-first iteration done with .list

    commentsList = []

    # for stickied threads
    for item in postList:
        id = item

        # submission = id
        submission = reddit.submission(id=id)

        # limit=None is all top-level comments
        submission.comments.replace_more(limit=2)

        # for testing
        # submission.comments.replace_more(limit=2)


        for comment in submission.comments.list():
            try: 
                #Going to run into Unicode Encode Errors for some comments TODO: Look into Unicode Encode Errors
                # must be some lame Windows thing
                commentsList.append(comment.body)
            except UnicodeEncodeError:
                #print(str(comment) + " couldn't be encoded.")
                with open(logPath, 'a') as f:
                    f.write(str(comment) + " couldn't be encoded.")
                    f.close()

    
    #return getTicker(commentsList)

    return commentsList
    #return getTicker(commentsList)


# In[44]:


commentsList = getComments(postList)
commentsList


# In[42]:


type(commentsList)


# In[43]:


df1 = pd.DataFrame({'comments':commentsList})
df1


# In[71]:


def getTicker(commentsList):
    # extract ticker symbols from comments
    # still needed with NYSE file because we really only want 3-5 character, usual tickers

    tickerList = []
    comments_found = []

    # credit: https://github.com/RyanElliott10/wsbtickerbot/blob/master/wsbtickerbot.py
    # common words on WSB to ignore
    
    blacklist_words = [
      "YOLO", "TOS", "CEO", "CFO", "CTO", "DD", "BTFD", "WSB", "OK", "RH",
      "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
      "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "PR", "PC", "ICE",
      "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
      "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
      "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
      "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
      "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG", "ALL", "OR"
      "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
      "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT", "WOW",
      "GG", "ELON", "GOP", "IPO", "WSB", "HIS", "THE", "ARK", "FUCK", "FOR",
        "EOD","SHORT","BURRY", "MMA","FOMC","CPI","FUCKA","RALLY","BOYS","SHIT",
        'COVID','DAMN','DOWN','JONES','HAS', 'AND','NOW','FAQ','STATS','JAPAN','CNBC',
        'INDEX','CHINA','PRICE','STATS','WHERE','NOW','YOU','STAND', 'TAKES',
        'THERE','SAYS','THAT','PEACE','TALKS','KYIV','MINSK','WOULD','HOLD','BTW',
        'SPAC','THIS','MUCH','FYI'
 
   ]
    

    #with open(commentsList) as c:
    for line in commentsList:
        match = re.findall(r'\b[A-Z]{3,5}\b[.!?]?',line)
        # if match contains data
        if match:
            # subtract from blacklist
            match = list(set(match) - set(blacklist_words))
            
            # filter out any non-chars and keep spaces
            # match is a list of strs from one line
            # https://stackoverflow.com/questions/55902042/python-keep-only-alphanumeric-and-space-and-ignore-non-ascii/55902074
            match = [re.sub(r'[^A-Za-z0-9 ]+', '', x) for x in match]

            for item in match:
                tickerList.append(item)
                comments_found.append(line)
                
                
    df2=pd.DataFrame({'Ticker':tickerList,'comment':comments_found})


    return df2
    #return validateTicker(tickerList)


# In[72]:


df2 = getTicker(commentsList)
df2





# In[75]:


def validateTicker():
    # test if it's a valid ticker

    # some issues with the list.. stuff like WOW and FOR and ALL and OR are included
    # TODO: Have file update when script runs and Alex tell me how you got it
    NYSETicker = "nyse_screener.txt" #Pre-generated file 
    
    validList = []
    validTicker = {}
    

    with open(NYSETicker, "r") as q:
        for line in q:
            validTicker[line.rstrip('\n')] = True
      

    for line in df2["Ticker"]: #Not O(N^2) because it is only one line
         for word in line.split():
            # attempt to validate ticker
            if validTicker.get(word, False):
                validList.append(word)
                    

    return validList
    #return database_insert(validList)


# In[76]:


validList = validateTicker()
validList


# In[163]:


def filtering_relevant_stocks():
    df2['validation'] = df2['Ticker'].isin(validList)
    df3 = df2[(df2.validation == True)]
    df4 = df3.groupby('Ticker')[['comment']].count().sort_values(by='comment',ascending=False).reset_index()
    df5 = list(df4['Ticker'][0:5])
    df3['top5'] = df3['Ticker'].isin(df5)
    df3 = df3[(df3["top5"]==True) & (df3["validation"]==True)]
    df3['id']=df3["Ticker"] + df3["comment"]
    return df3


# In[164]:


df3 = filtering_relevant_stocks()


# In[165]:


df3

