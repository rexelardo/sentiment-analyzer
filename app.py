import urllib.request, json 
from jinja2 import Environment, FileSystemLoader
import pandas as pd

tickers = ''
price_df = {'tickers':[], 'price':[], "percent_change":[],\
    'market_cap':[], 'vol_24h':[], 'id':[]}
for i in range(1, 11):
    endpoint = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={i}&sparkline=false'

    with urllib.request.urlopen(endpoint) as url:
        data = json.loads(url.read().decode())
        for crypto in data:
            tickers = tickers + "'" + crypto['symbol'].upper() + "'" + ','
            price_df['tickers'].append(crypto['symbol'].upper())
            price_df['price'].append(crypto['current_price'])
            price_df['percent_change'].append(crypto['price_change_percentage_24h'])
            price_df['market_cap'].append(crypto['market_cap'])
            price_df['vol_24h'].append(crypto['total_volume'])
            price_df['id'].append(crypto['id'])
file_loader = FileSystemLoader('./')
env = Environment(loader=file_loader)
template = env.get_template('data.jinja2')
output = template.render(tickers=tickers)
with open("data.py", "w") as fh:
    fh.write(output)


prices = pd.DataFrame(price_df).set_index('tickers')
prices = prices.rename_axis(None)
prices.to_csv('prices.csv')


'''*****************************************************************************
Purpose: To analyze the sentiments of the reddit
This program uses Vader SentimentIntensityAnalyzer to calculate the ticker compound value. 
You can change multiple parameters to suit your needs. See below under "set program parameters."
Implementation:
I am using sets for 'x in s' comparison, sets time complexity for "x in s" is O(1) compare to list: O(n).
Limitations:
It depends mainly on the defined parameters for current implementation:
It completely ignores the heavily downvoted comments, and there can be a time when
the most mentioned ticker is heavily downvoted, but you can change that in upvotes variable.
-------------------------------------------------------------------
****************************************************************************'''

import praw
from data import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from nltk.sentiment.vader import SentimentIntensityAnalyzer

start_time = time.time()
reddit = praw.Reddit(
    user_agent='Comment Extraction',
    client_id='XaAXvHIxw-U9Gw',
    client_secret='R6NkwcVi9o_NjkBqsAZzLWfxgLflLw'
)

'''############################################################################'''
# set the program parameters
subs = ['CryptoCurrency', 'CryptoMarkets']     # sub-reddit to search
submission_name = ('Daily Discussion','Weekly Discussion Megathread') # posts title to search
goodAuth = {'AutoModerator'}   # authors whom comments are allowed more than once
uniqueCmt = True                # allow one comment per author per symbol
ignoreAuthP = {'example'}       # authors to ignore for posts 
ignoreAuthC = {'example'}       # authors to ignore for comment 
upvoteRatio = 0.70         # upvote ratio for post to be considered, 0.70 = 70%
ups = 20       # define # of upvotes, post is considered if upvotes exceed this #
limit = 100      # define the limit, comments 'replace more' limit
upvotes = 2     # define # of upvotes, comment is considered if upvotes exceed this #
picks = 10     # define # of picks here, prints as "Top ## picks are:"
picks_ayz = 20   # define # of picks for sentiment analysis
'''############################################################################'''

posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
cmt_auth = {}

for sub in subs:
    subreddit = reddit.subreddit(sub)
    hot_python = subreddit.hot()    # sorting posts by hot
    # Extracting comments, symbols from subreddit
    for submission in hot_python:
        # checking: post upvote ratio # of upvotes, post flair, and author 
        if submission.title.startswith(submission_name):   
            submission.comment_sort = 'new'     
            comments = submission.comments
            titles.append(submission.title)
            posts += 1
            submission.comments.replace_more(limit=limit)   
            for comment in comments:
                #print(comment.body)
                #print(comment.score)
                # try except for deleted account?
                try: auth = comment.author.name
                except: pass
                c_analyzed += 1
                
                # checking: comment upvotes and author
                if comment.score > upvotes and auth not in ignoreAuthC:      
                    split = comment.body.split(" ")
                    for word in split:
                        word = word.replace("$", "")        
                        # upper = ticker, length of ticker <= 5, excluded words,                     
                        #print(word)
                        if word.isupper() and len(word) <= 5 and word not in blacklist and word in crypto:
                            #print('here')
                            
                            # unique comments, try/except for key errors
                            if uniqueCmt and auth not in goodAuth:
                                try: 
                                    if auth in cmt_auth[word]: break
                                except: pass
                                
                            # counting tickers
                            if word in tickers:
                                tickers[word] += 1
                                a_comments[word].append(comment.body)
                                cmt_auth[word].append(auth)
                                count += 1
                            else:                               
                                tickers[word] = 1
                                cmt_auth[word] = [auth]
                                a_comments[word] = [comment.body]
                                count += 1    

# sorts the dictionary
symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse = True))
top_picks = list(symbols.keys())[0:picks]
time = (time.time() - start_time)

# print top picks
print("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time, c=c_analyzed, p=posts, s=len(subs)))
print("Posts analyzed saved in titles")
#for i in titles: print(i)  # prints the title of the posts analyzed

print(f"\n{picks} most mentioned picks: ")
print(top_picks)
times = []
top = []
for i in top_picks:
    print(f"{i}: {symbols[i]}")
    times.append(symbols[i])
    top.append(f"{i}: {symbols[i]}")
   
    
# Applying Sentiment Analysis
scores, s = {}, {}
 
vader = SentimentIntensityAnalyzer()
# adding custom words from data.py 
vader.lexicon.update(new_words)

picks_sentiment = list(symbols.keys())[0:picks_ayz]
for symbol in picks_sentiment:
    stock_comments = a_comments[symbol]
    for cmnt in stock_comments:
        score = vader.polarity_scores(cmnt)
        if symbol in s:
            s[symbol][cmnt] = score
        else:
            s[symbol] = {cmnt:score}      
        if symbol in scores:
            for key, _ in score.items():
                scores[symbol][key] += score[key]
        else:
            scores[symbol] = score
            
    # calculating avg.
    for key in score:
        scores[symbol][key] = scores[symbol][key] / symbols[symbol]
        scores[symbol][key]  = "{pol:.3f}".format(pol=scores[symbol][key])

# printing sentiment analysis 
print(f"\nSentiment analysis of top {picks_ayz} picks:")
df = pd.DataFrame(scores)
df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
df = df.T
df.to_csv('sentiment.csv')
print(df)

# Date Visualization
# most mentioned picks    
squarify.plot(sizes=times, label=top, alpha=.7 )
plt.axis('off')
plt.title(f"{picks} most mentioned picks")
plt.savefig('squares.png')
plt.show()


# Sentiment analysis
df = df.astype(float)
colors = ['red', 'springgreen', 'forestgreen', 'coral']
df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {picks_ayz} picks:")
plt.savefig('barchart.png')
plt.show()


import streamlit as st

import numpy as np
import pandas as pd

st.markdown("""# Crypto sentiment Analyzer
## Let's get the sentiments!""")


# and used in order to select the displayed lines
sentiment = pd.read_csv('sentiment.csv')
sentiment = sentiment.sort_values(by=['Unnamed: 0'], ascending=True)
prices = pd.read_csv('prices.csv') 
prices = prices[prices['Unnamed: 0'].isin(sentiment['Unnamed: 0'])]
prices = prices.drop_duplicates(subset=['Unnamed: 0']).fillna(0)
prices = prices.sort_values(by=['Unnamed: 0'], ascending=True)
a = sentiment['Total/Compound'].to_list()
prices['Total/Compound'] = a
color = []
for i in sentiment['Total/Compound']:
    print(i)
    if i >=  0 and i < 0.2:
        color.append('orange')
    elif i >= 0.2:
        color.append('green')
    elif i<0:
        color.append('red')
sentiment['color'] = color
b = sentiment['color'].to_list()
prices['color'] = b


def color_positive_green(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: green'` for positive
    strings, black otherwise.
    """
    if val == 'orange':
        color = 'orange'
    elif val == 'red':
        color = 'red'
    elif val =='green':
        color = 'green'
    return 'background-color: %s' % color


 

final_chart =  prices.style.applymap(color_positive_green, subset=['color'])
final_chart
st.markdown("# chart with price movement of top 2500 cryptos by marketcap (according to coingecko)")


all_prices = pd.read_csv('prices.csv')
all_prices

st.markdown("""# Now we show the charts
## chart showing most spoken about cryptos at the moment:""")

st.image('squares.png')

st.markdown('## barchart showing the sentiments')
st.image('barchart.png')
