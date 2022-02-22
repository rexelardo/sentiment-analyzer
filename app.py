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
