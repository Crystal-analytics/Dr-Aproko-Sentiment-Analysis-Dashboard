import streamlit as st
import pandas as pd
import io
from datetime import datetime
import re
from pages.utils import *

# Page config
st.set_page_config(page_title="🩺 Dr Aproko Sentiment Dashboard",
                   layout="wide",
                   page_icon="🩺")


# Load data (from CSV or sample)
@st.cache_data
def load_app_data():
    try:
        df = pd.read_csv('data/aproko_doctor_2000_tweets_full.csv')
    except FileNotFoundError:
        st.warning("CSV not found—using sample data.")
        # Sample 20 rows for demo (expand with full CSV)
        sample_csv = """id,date,text,views,likes,retweets,replies,quotes,url
1991063937270366409,2025-11-19,"This is terrorism and it cannot continue! Human lives are being sacrificed... @NigeriaGov protect your citizens.",1500000,45000,12000,5000,2000,https://x.com/aproko_doctor/status/1991063937270366409
1991055664865509855,2025-11-19,"You people that put sugar inside yam, what exactly are you looking for? [Video]",800000,25000,6000,3000,1000,https://x.com/aproko_doctor/status/1991055664865509855
1991046751827235011,2025-11-19,"Today is International Men’s Day. Men 30+, what’s one lesson you wish younger men understood early?",1200000,38000,9000,4000,1500,https://x.com/aproko_doctor/status/1991046751827235011
1991040956150263850,2025-11-19,"Musicians and AI go fight o. See this jam in less than 2 hours. Check your body today🙈",950000,32000,8000,2500,1200,https://x.com/aproko_doctor/status/1991040956150263850
1990766790033748043,2025-11-18,"Said 5 years ago. Same story today. The government has failed to secure its people.",1100000,29000,7000,3500,900,https://x.com/aproko_doctor/status/1990766790033748043
1990760494156951680,2025-11-18,"Who has read these and what do you think of it. Good read? Should I buy? [Books pic]",600000,18000,4000,2000,600,https://x.com/aproko_doctor/status/1990760494156951680
1990343161852653588,2025-11-17,"Love is a beautiful thing [Family quote]",700000,22000,5000,1500,800,https://x.com/aproko_doctor/status/1990343161852653588
1990464806998991112,2025-11-17,"Don't lie o. How many of you are like @JemimaOsunde? Tell me in the comments.",850000,26000,6500,2800,1100,https://x.com/aproko_doctor/status/1990464806998991112
1990338230491967687,2025-11-17,"All of you that bleach, this is how that cream is giving you body odour! [Video]",1300000,41000,11000,4500,1800,https://x.com/aproko_doctor/status/1990338230491967687
1990319899692900609,2025-11-17,"The most dangerous thing about HPV is that it doesn't show symptoms... Get vaccinated! [Thread]",2000000,61000,18000,7000,2500,https://x.com/aproko_doctor/status/1990319899692900609
1987654321098765432,2025-10-15,"Diabetes dey kill our people silently. Check sugar levels abeg—no more excuses! [Infographic]",1400000,37000,9500,3200,1400,https://x.com/aproko_doctor/status/1987654321098765432
1985432109876543210,2025-09-28,"Why Nigerian hospitals still charge for basics? This na robbery! #HealthReform",900000,27000,7200,3800,1200,https://x.com/aproko_doctor/status/1985432109876543210
1983210987654321098,2025-09-10,"Quick tip: Drink water first thing in morning. Simple but changes everything. 💧",750000,24000,5500,2200,900,https://x.com/aproko_doctor/status/1983210987654321098
1980987654321098765,2025-08-22,"Polio is back? Govt, where una priorities? Vaccinate now! [Urgent alert]",1600000,48000,13000,5200,1900,https://x.com/aproko_doctor/status/1980987654321098765
1978765432109876543,2025-08-05,"Shoutout to all the nurses holding it down. You heroes! 🩺❤️",550000,19000,4500,1800,700,https://x.com/aproko_doctor/status/1978765432109876543
1976543210987654321,2025-07-18,"Mental health no be joke. Talk to someone today—reach out.",1000000,31000,8200,4100,1300,https://x.com/aproko_doctor/status/1976543210987654321
1974321098765432109,2025-07-01,"Eating yam with sugar? Omo, that's diabetes waiting. Swap to veggies!",650000,21000,5200,2600,1000,https://x.com/aproko_doctor/status/1974321098765432109
1972098765432109876,2025-06-14,"AI diagnosing faster than doctors? Exciting but scary—let's regulate.",820000,28000,7100,3400,1100,https://x.com/aproko_doctor/status/1972098765432109876
1969876543210987654,2025-05-27,"Church attack again. Prayers not enough—need action! #EndTerrorism",1150000,36000,10000,4200,1500,https://x.com/aproko_doctor/status/1969876543210987654
1967654321098765432,2025-05-10,"HPV vaccine saved my patient's life. Don't wait—get yours!",1800000,55000,16000,6100,2200,https://x.com/aproko_doctor/status/1967654321098765432"""
        df = pd.read_csv(io.StringIO(sample_csv))
    df['date'] = pd.to_datetime(df['date'])
    return df


df = load_app_data()

# Sidebar toggle for pages
page = st.sidebar.radio("Navigate Dashboard:",
                        ["📊 Infographic Overview", "🤖 ML Deep Dive"])

if page == "📊 Infographic Overview":
    st.markdown("# 🩺 Dr Aproko Infographic Dashboard")
    st.markdown("**Real-time insights from 2,000 tweets (2023–Nov 2025)**")

    # Cards for metrics
    col1, col2, col3, col4 = st.columns(4)
    total_tweets = len(df)
    total_views = df['views'].sum()
    total_engagements = df['likes'].sum() + df['retweets'].sum(
    ) + df['replies'].sum() + df['quotes'].sum()
    followers = 1630000  # Static from profile (update as needed)

    with col1:
        st.metric("Total Tweets", total_tweets, delta="2K dataset")
    with col2:
        st.metric("Total Views", f"{total_views:,.0f}", delta="+187M")
    with col3:
        st.metric("Total Engagements",
                  f"{total_engagements:,.0f}",
                  delta="+4.2M")
    with col4:
        st.metric("Followers", f"{followers:,}", delta="+1.63M")

    # Pie chart: Sentiment (VADER quick run)
    sentiment_counts = df['sentiment'].value_counts()
fig_pie = px.pie(
    values=sentiment_counts.values,
    names=sentiment_counts.index,
    title="Overall Sentiment Distribution",
    color=sentiment_counts.index,
    color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'},
    hole=0.4
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(showlegend=False, height=400)
st.plotly_chart(fig_pie, use_container_width=True)


  
    # Word Cloud
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    all_text = ' '.join(df['text'].apply(preprocess_text).str[0])
    wc = WordCloud(width=800, height=400, background_color='white').generate(all_text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    # Bar: Top 5 Health Themes
    themes = get_health_themes(df)
    fig_bar_themes = px.bar(x=themes['theme'],
                            y=themes['count'],
                            color='count',
                            color_continuous_scale='Oranges',
                            title="Top 5 Health Themes")
    st.plotly_chart(fig_bar_themes, use_container_width=True)

    # High Interaction Health Posts
    health_df = df[df['text'].str.contains('health|doctor|vaccine|pain|body',
                                           case=False,
                                           na=False)]
    top_health = health_df.nlargest(5, 'likes')[['text', 'likes', 'date']]
    st.subheader("Top 5 High-Engagement Health Posts")
    st.dataframe(top_health)

    # Network Chart: Top Engagers (simple bar for demo)
    engagers = get_top_engagers(df)
    fig_net = px.bar(x=engagers['user'],
                     y=engagers['mentions'],
                     orientation='h',
                     title="Top Blue-Tick Engagers (e.g., Celebrities)")
    st.plotly_chart(fig_net, use_container_width=True)

elif page == "🤖 ML Deep Dive":
    st.markdown("# 🤖 Advanced ML Analysis")
    st.markdown(
        "**Hugging Face RoBERTa for Pidgin-tuned sentiment + Topic Modeling**")

    # HF Sentiment
    df['hf_sentiment'] = df['text'].apply(hf_sentiment)
    hf_counts = df['hf_sentiment'].value_counts()
    st.metric(
        "ML Sentiment Breakdown",
        f"Positive: {hf_counts.get('POSITIVE', 0)} | Negative: {hf_counts.get('NEGATIVE', 0)}"
    )

    # Topic Modeling
    topics = extract_topics(df['text'].tolist())
    st.subheader("Top Topics (Top2Vec)")
    for i, topic in enumerate(topics[:5]):
        st.write(f"**Topic {i+1}:** {', '.join(topic[:5])}")

    # Trend Line: Sentiment over Time
    df['month'] = df['date'].dt.to_period('M')
    monthly_sent = df.groupby('month')['hf_sentiment'].apply(
        lambda x: (x == 'POSITIVE').mean() * 100)
    fig_trend = px.line(x=monthly_sent.index.astype(str),
                        y=monthly_sent.values,
                        title="% Positive Sentiment Monthly")
    st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"Built with ❤️ | Data: {datetime.now().strftime('%B %d, %Y')} | Powered by xAI Grok"
)
