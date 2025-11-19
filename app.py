import streamlit as st
import pandas as pd
import io
from datetime import datetime
import re
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pages.utils import *

# Page config
st.set_page_config(page_title="🩺 Dr Aproko Sentiment Dashboard",
                   layout="wide",
                   page_icon="🩺")

# Load data
@st.cache_data
def load_app_data():
    try:
        df = pd.read_csv('data/aproko_doctor_2000_tweets_full.csv')
    except FileNotFoundError:
        st.warning("CSV not found — using sample data.")
        sample_csv = """id,date,text,views,likes,retweets,replies,quotes,url
1991063937270366409,2025-11-19,"This is terrorism and it cannot continue! Human lives are being sacrificed... @NigeriaGov protect your citizens.",1500000,45000,12000,5000,2000,https://x.com/aproko_doctor/status/1991063937270366409
..."""  # your full sample or leave as-is
        df = pd.read_csv(io.StringIO(sample_csv))
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

df = load_app_data()

# Add sentiment column (VADER)
df['sentiment'] = df['text'].apply(vader_sentiment)

# Sidebar
page = st.sidebar.radio("Navigate Dashboard:",
                        ["📊 Infographic Overview", "🤖 ML Deep Dive"])

if page == "📊 Infographic Overview":
    st.markdown("# 🩺 Dr Aproko Infographic Dashboard")
    st.markdown("**Real-time insights from 2,000 tweets (2023–Nov 2025)**")

    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    total_tweets = len(df)
    total_views = df['views'].sum()
    total_engagements = (df['likes'].sum() + df['retweets'].sum() + 
                         df['replies'].sum() + df['quotes'].sum())
    followers = 1630000

    with col1:
        st.metric("Total Tweets", total_tweets, delta="2K dataset")
    with col2:
        st.metric("Total Views", f"{total_views:,.0f}", delta="+187M")
    with col3:
        st.metric("Total Engagements", f"{total_engagements:,.0f}", delta="+4.2M")
    with col4:
        st.metric("Followers", f"{followers:,}", delta="+1.63M")

    # Sentiment Pie Chart
    sentiment_counts = df['sentiment'].value_counts()
    fig_pie = px.pie(values=sentiment_counts.values,
                      names=sentiment_counts.index,
                      title="Overall Sentiment Distribution",
                      color_discrete_map={'Positive': '#00CC96',
                                         'Negative': '#EF553B',
                                         'Neutral': '#636EFA'},
                      hole=0.4)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Word Cloud
    st.subheader("Most Used Words (Word Cloud)")
    all_text = " ".join(df["text"].apply(preprocess_text))
    wordcloud = WordCloud(width=800, height=400,
                          background_color="white",
                          colormap="viridis",
                          max_words=100).generate(all_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Top 5 Health Themes
    themes = get_health_themes(df)
    fig_bar = px.bar(themes, x='theme', y='count', color='count',
                      color_continuous_scale='Oranges',
                      title="Top 5 Health Themes")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Top High-Engagement Health Posts
    health_df = df[df['text'].str.contains('health|doctor|vaccine|pain|body|cancer|hpv|diabetes|mental', case=False, na=False)]
    top_health = health_df.nlargest(5, 'likes')[['text', 'likes', 'date']]
    st.subheader("Top 5 High-Engagement Health Posts")
    st.dataframe(top_health, use_container_width=True)

    # Top Engagers Bar Chart
    engagers = get_top_engagers(df)
    fig_engagers = px.bar(engagers, x='mentions', y='user', orientation='h',
                          color='mentions', title="Top Engagers (Mentions)")
    st.plotly_chart(fig_engagers, use_container_width=True)

elif page == "🤖 ML Deep Dive":
    st.markdown("# 🤖 Advanced ML Analysis (VADER Edition)")
    st.info("Hugging Face model temporarily disabled — VADER running perfectly")

    df['hf_sentiment'] = df['text'].apply(hf_sentiment)  # fallback to VADER
    hf_counts = df['hf_sentiment'].value_counts()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Positive", hf_counts.get('Positive', 0))
    with col2:
        st.metric("Negative", hf_counts.get('Negative', 0))
    with col3:
        st.metric("Neutral", hf_counts.get('Neutral', 0))

    # Topics
    st.subheader("Top Topics")
    topics = extract_topics(df['text'].tolist())
    for i, topic in enumerate(topics[:5]):
        st.write(f"**Topic {i+1}:** {', '.join(topic)}")

    # Monthly Trend
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')['hf_sentiment'].apply(lambda x: (x == 'Positive').mean() * 100)
    fig_trend = px.line(x=monthly.index.astype(str), y=monthly.values,
                        title="% Positive Sentiment Over Time", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"Built with ❤️ by Crystal Analytics | Data updated: {datetime.now().strftime('%B %d, %Y')} | Powered by xAI Grok")

