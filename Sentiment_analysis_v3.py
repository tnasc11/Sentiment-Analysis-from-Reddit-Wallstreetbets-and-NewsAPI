#!/usr/bin/env python
# coding: utf-8

# In[1]:


#basic
import pandas as pd
import torch
from Reddit_scraper_v4 import df3

#transformers
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from transformers import pipeline

#preventing warnings
pd.options.mode.chained_assignment = None


# In[2]:


from scipy.special import softmax
import numpy
import yfinance as yf
from tqdm.notebook import tqdm


# In[3]:


df3.reset_index(drop=True,inplace=True)
df3.head()


# In[4]:


stocks = list(set(df3['Ticker']))
stocks


# In[5]:



#MODEL = 'ProsusAI/finbert'
MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
 


# In[6]:


comments = list(df3['comment'])
comments


# In[7]:


def get_sentiment(comments):
    encoded_text = tokenizer(comments, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'reddit_neg': scores[0],
        'reddit_neu': scores[1],
        'reddit_pos': scores[2]
    }
    return scores_dict


# In[9]:


sent_results=[]

for index in df3.index:
    sent = get_sentiment(df3.loc[index,'comment'])
    sent_results.append(sent)


# In[10]:


print(sent_results)


# In[11]:


df=pd.DataFrame(sent_results)


# In[12]:


df.head()


# In[13]:


result = pd.concat([df3, df], axis=1)


# In[14]:


result


# In[15]:


final_df_short = result.groupby(by='Ticker',axis=0).mean()
final_df_short.drop(['validation','top5'],axis=1,inplace=True)
final_df_short

