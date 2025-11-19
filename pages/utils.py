# pages/utils.py   ← make sure this file is inside the "pages" folder!

import pandas as pd
import re
import nltk
import streamlit as st                     # ← THIS WAS MISSING!
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from top2vec import Top2Vec

# Download once (quietly)
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# ────────────────────── Hugging Face Model (cached) ──────────────────────
@st.cache_resource(show_spinner="Loading AI sentiment model (first time only, ~30–60 sec)...")
def load_hf_pipeline():
    return pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
        device=-1  # CPU only – Streamlit Cloud has no GPU
    )

# Load once and reuse forever
hf_pipeline = load_hf_pipeline()
# ────────────────────── Helper Functions ──────────────────────
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
def hf_sentiment(text):
    try:
        cleaned = preprocess_text(text)[:512]  # model limit
        result = hf_pipeline(cleaned)[0]
        label = result['label']
        # The model returns LABEL_0 (neg), LABEL_1 (neu), LABEL_2 (pos)
        if label == "LABEL_2":
            return "POSITIVE"
        elif label == "LABEL_0":
            return "NEGATIVE"
        else:
            return "NEUTRAL"
    except:
        return "NEUTRAL"
def extract_topics(texts, num_topics=5):
    try:
        model = Top2Vec(documents=texts, embedding_model='universal-sentence-encoder')
        topic_words, _, _ = model.get_topics(num_topics)
        return [words.tolist()[:5] for words in topic_words]
    except:
        return [["health", "body", "doctor", "vaccine", "cancer"]]
def get_health_themes(df):
    themes = {
        'HPV/Cervical Cancer': len(df[df['text'].str.contains('hpv|cervical|cancer', case=False, na=False)]),
        'Diabetes': len(df[df['text'].str.contains('diabetes|sugar', case=False, na=False)]),
        'Mental Health': len(df[df['text'].str.contains('mental|depress|anxiety', case=False, na=False)]),
        'Vaccines': len(df[df['text'].str.contains('vaccine|immun|polio', case=False, na=False)]),
        'General Wellness': len(df[df['text'].str.contains('health|body|pain|sleep|water', case=False, na=False)])
    }
    return (pd.DataFrame(themes.items(), columns=['theme', 'count'])
              .sort_values('count', ascending=False)
              .head(5))
def get_top_engagers(df):
    mentions = df['text'].str.extractall(r'(@[A-Za-z0-9_]+)')
    if mentions.empty:
        return pd.DataFrame({'user': ['@example'], 'mentions': [0]})
    top = mentions.groupby(0).size().sort_values(ascending=False).head(10)
    return pd.DataFrame({'user': top.index, 'mentions': top.values})

