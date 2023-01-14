#!/usr/bin/env python
# coding: utf-8

# In[57]:





# In[1]:


#from sentiment_analysis import final_df_short
import pandas as pd
from newsapi import NewsApiClient
from NewsAPIcredentials import api_key
import requests
from datetime import datetime, timedelta
from Sentiment_analysis_v3 import final_df_short
#preventing warnings
pd.options.mode.chained_assignment = None
#sentiment
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from scipy.special import softmax
import matplotlib as plt
import numpy as np

# In[2]:


final_df_short


# Dataprep

# In[5]:


def dataprep():
    data = pd.read_csv('nasdaq_screener_big_1.csv')
    data.rename(columns={'Symbol':'Ticker'}, inplace=True)
    final_df_short.reset_index(inplace=True)
    df_updated=pd.merge(final_df_short,data, on='Ticker', how='left')
    df_updated.drop(columns=df_updated.columns[-9:], axis=1, inplace=True)
    first_name = [df_updated.Name.str.split(' ')[index][0]
             for index in range(0, len(df_updated))]
    df_updated['first name'] = first_name
    return df_updated


# In[6]:


df_updated = dataprep()
df_updated


# In[13]:


yesterday = datetime.now() - timedelta(2)
yesterday = datetime.strftime(yesterday, '%Y-%m-%d')
yesterday


# In[14]:


stocks = list(df_updated['Ticker'])
stock_name = list(df_updated['first name'])


# In[15]:


stocks


# In[16]:


# NewsAPI
newsapi = NewsApiClient(api_key)

k = list(zip(stocks, stock_name))
d={}
articles=[]

for (x, y) in k:
    news = newsapi.get_everything(
        q=f'{x} AND {y}',
        language='en',
        from_param=str(yesterday),
        sort_by='relevancy')
    articles = news['articles']
    articles = pd.DataFrame(articles)
    articles = articles['content']
    d[x]=articles


# In[17]:


d


# In[12]:


df = pd.DataFrame(d)
df


# In[18]:


df = pd.melt(df, var_name="Ticker", value_name="content")


# In[19]:


df = df.dropna()


# In[20]:


df.reset_index(drop=True,inplace=True)


# In[21]:


MODEL = 'ProsusAI/finbert'
#MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


# In[22]:


content = list(df['content'])


# In[23]:


content


# In[24]:


def get_sentiment(content):
    encoded_text = tokenizer(content, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'news_neg': scores[0],
        'news_neu': scores[1],
        'news_pos': scores[2]
    }
    return scores_dict


# In[25]:


sent_results=[]

for index in df.index:
    sent = get_sentiment(df.loc[index,'content'])
    sent_results.append(sent)


# In[26]:


df1 = pd.DataFrame(sent_results)
df1


# In[28]:


result = pd.concat([df, df1], axis=1)
result


# In[29]:


final_result = result.groupby(by='Ticker',axis=0).mean()
final_result.reset_index(drop=False,inplace=True)
final_result


# In[30]:


combined_dfs = pd.concat([final_result, final_df_short], axis=1,copy=False)


# In[31]:


combined_dfs = pd.merge(final_result, final_df_short, on=["Ticker"], how="left")


# In[66]:


combined_dfs = combined_dfs.drop('index',axis=1)
combined_dfs


# In[65]:


# Values of each group
bars1 = combined_dfs['reddit_neg']
bars2 = combined_dfs['reddit_neu']
bars3 = combined_dfs['reddit_pos']
 
# Heights of bars1 + bars2
bars = np.add(bars1, bars2).tolist()
 
# The position of the bars on the x-axis
r = [0,1,2,3,4]
 
# Names of group and bar width
names = list(set(combined_dfs['Ticker']))
barWidth = 1
 
# Create brown bars
plt.bar(r, bars1, color='#ff6961' , edgecolor='white', width=barWidth/2)
# Create green bars (middle), on top of the first ones
plt.bar(r, bars2, bottom=bars1, color='#A9A9A9', edgecolor='white', width=barWidth/2)
# Create green bars (top)
plt.bar(r, bars3, bottom=bars, color='#85BB65', edgecolor='white', width=barWidth/2)
 
# Custom X axis
plt.xticks(r, names,)
 
# Show graphic
plt.show()

