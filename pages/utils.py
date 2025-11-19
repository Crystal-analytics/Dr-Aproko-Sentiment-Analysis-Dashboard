import pandas as pd
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from top2vec import Top2Vec
import nltk

nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()
hf_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest")


def preprocess_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    return text.lower()


def vader_sentiment(text):
    scores = sia.polarity_scores(preprocess_text(text))
    compound = scores['compound']
    if compound >= 0.05: return 'Positive'
    elif compound <= -0.05: return 'Negative'
    else: return 'Neutral'


def hf_sentiment(text):
    try:
        result = hf_pipeline(preprocess_text(text))[0]
        return result['label']
    except:
        return 'Neutral'  # Fallback


def extract_topics(texts, num_topics=5):
    model = Top2Vec(documents=texts,
                    embedding_model='universal-sentence-encoder')
    topics, _ = model.get_topics(num_topics)
    return [model.get_topic_words(i) for i in range(num_topics)]


def get_health_themes(df):
    themes = {
        'HPV/Cervical Cancer':
        len(df[df['text'].str.contains('hpv|cervical|cancer', case=False)]),
        'Diabetes':
        len(df[df['text'].str.contains('diabetes|sugar', case=False)]),
        'Mental Health':
        len(df[df['text'].str.contains('mental|depress|anxiety', case=False)]),
        'Vaccines':
        len(df[df['text'].str.contains('vaccine|immun|polio', case=False)]),
        'General Wellness':
        len(df[df['text'].str.contains('health|body|pain|sleep', case=False)])
    }
    return pd.DataFrame(list(themes.items()),
                        columns=['theme',
                                 'count']).sort_values('count',
                                                       ascending=False).head(5)


def get_top_engagers(df):
    # Simple regex for mentions (blue-tick sim: assume top are celebs)
    engagers = df['text'].str.extractall(r'(@[A-Za-z0-9_]+)').groupby(
        level=0).count().sum().sort_values(ascending=False).head(10)
    return pd.DataFrame({
        'user': engagers.index,
        'mentions': engagers.values
    }).reset_index(drop=True)

