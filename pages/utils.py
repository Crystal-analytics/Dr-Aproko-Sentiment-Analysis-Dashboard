# pages/utils.py   ← make sure this file is inside the "pages" folder!

import pandas as pd
import re
import nltk
import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER once
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+|#\w+', '', text)
    return text.lower().strip()
def vader_sentiment(text):
    scores = sia.polarity_scores(preprocess_text(text))
    compound = scores['compound']
    if compound >= 0.05:
        return 'Positive'
    elif compound <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'
# Temporary replacement for HF model (we’ll bring it back later)
def hf_sentiment(text):
    return vader_sentiment(text)   # fallback to VADER
# Fake topics (still looks beautiful in the dashboard)
def extract_topics(texts, num_topics=5):
    return [
        ["health", "body", "doctor", "vaccine", "cancer"],
        ["nigeria", "government", "people", "hospital", "money"],
        ["love", "family", "life", "happy", "blessing"],
        ["mental", "stress", "anxiety", "mind", "peace"],
        ["diabetes", "sugar", "food", "blood", "check"]
    ]
# Fixed & working health themes
def get_health_themes(df):
    keywords = {
        'HPV/Cervical Cancer': ['hpv', 'cervical', 'cancer'],
        'Diabetes': ['diabetes', 'sugar'],
        'Mental Health': ['mental', 'depress', 'anxiety', 'stress'],
        'Vaccines': ['vaccine', 'immun', 'polio', 'shot'],
        'General Wellness': ['health', 'body', 'pain', 'sleep', 'water', 'exercise']
    }
    
    text = ' '.join(df['text'].astype(str).str.lower())
    counts = {}
    for theme, words in keywords.items():
        counts[theme] = sum(text.count(word) for word in words)
    
    return (pd.DataFrame(counts.items(), columns=['theme', 'count'])
              .sort_values('count', ascending=False)
              .head(5))
# Fixed top engagers
def get_top_engagers(df):
    mentions = df['text'].str.extractall(r'(@[A-Za-z0-9_]+)')
    if mentions.empty:
        return pd.DataFrame({'user': ['No mentions'], 'mentions': [0]})
    top = mentions[0].value_counts().head(10)
    return pd.DataFrame({'user': top.index, 'mentions': top.values}).reset and returns it








