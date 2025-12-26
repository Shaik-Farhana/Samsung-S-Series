import streamlit as st
import pandas as pd
import os

# ===== CUSTOM CSS FOR BEAUTIFUL STYLING =====
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background: linear-gradient(to bottom, #0e1117, #1a1f2e);
    }
    h1, h2, h3 {
        color: #6e48ff !important;  /* Samsung-inspired purple-blue */
        font-weight: 700;
    }
    .highlight-card {
        background-color: #1e2235;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #6e48ff;
        box-shadow: 0 4px 15px rgba(110, 72, 255, 0.2);
        margin: 15px 0;
    }
    .best-phone {
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        color: black !important;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }
    .metric-label {
        color: #a0a0a0;
        font-size: 0.9em;
    }
    .metric-value {
        color: #6e48ff;
        font-size: 1.4em;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #6e48ff;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #5538cc;
    }
</style>
""", unsafe_allow_html=True)

# Load data
csv_path = 'data/combined_samsung_data.csv'
if not os.path.exists(csv_path):
    st.error("⚠️ Run `python data_collector.py` first to load phone data!")
    st.stop()

df = pd.read_csv(csv_path)

# ===== TITLE & HERO SECTION =====
st.title("🏆 Samsung Galaxy S Series Dashboard")

st.markdown("""
<div style='text-align: center; font-size: 1.4em; color: #ffd700; margin: 20px 0; padding: 20px;'>
    Made it for you 😭<br>
    Be happy, huh... UNGRATEFULL POTATOOOO!!!!!
</div>
""", unsafe_allow_html=True)

# ===== POPULARITY BAR CHART =====
st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.subheader("📊 Popularity Ranking (Combined Amazon + Flipkart Reviews)")

chart_df = df.sort_values('popularity_score', ascending=False)

st.bar_chart(
    data=chart_df,
    x='model_name',
    y='popularity_score',
    use_container_width=True,
    height=500,
    color='#6e48ff'  # Purple bars
)
st.caption("💡 Higher bar = More popular (based on total reviews × rating)")
st.markdown("</div>", unsafe_allow_html=True)

# ===== BUDGET FILTER =====
st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.subheader("💰 Set Your Budget")
max_price = int(df['price_inr'].max())
budget = st.slider("Choose max price (₹ INR)", 20000, max_price + 50000, 0, 5000, key="budget")

if budget > 0:
    filtered_df = df[df['price_inr'] <= budget]
    st.success(f"Showing {len(filtered_df)} phones under ₹{budget:,}")
else:
    filtered_df = df
    st.info("Showing all S series phones")

filtered_df = filtered_df.sort_values('popularity_score', ascending=False)
st.markdown("</div>", unsafe_allow_html=True)

# ===== COMPARISON TABLE =====
st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.subheader("📱 Compare Phones")
st.dataframe(
    filtered_df[['model_name', 'price_inr', 'rating_amazon', 'review_count_amazon',
                'rating_flipkart', 'review_count_flipkart', 'best_2025_flag']],
    use_container_width=True,
    hide_index=True
)
st.markdown("</div>", unsafe_allow_html=True)

# ===== DETAILED PHONE VIEW =====
st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.subheader("🔍 View Full Details")
selected = st.selectbox("Select a phone", filtered_df['model_name'])
phone = df[df['model_name'] == selected].iloc[0]

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### {phone['model_name']} 🚀")
    st.markdown(f"<p class='metric-value'>₹{phone['price_inr']:,}</p><p class='metric-label'>Current Price</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>{phone['rating_amazon']} ⭐ ({phone['review_count_amazon']:,} Amazon)</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>{phone['rating_flipkart']} ⭐ ({phone['review_count_flipkart']:,} Flipkart)</p>", unsafe_allow_html=True)
    
    st.markdown("**Buy Now:**")
    st.link_button("🛒 Amazon India", phone['url_amazon'])
    st.link_button("🛍️ Flipkart", phone['url_flipkart'])

with col2:
    st.markdown("**Specs**")
    st.write(f"**Processor**: {phone['processor']}")
    st.write(f"**OS**: {phone['os_version']}")
    st.write(f"**Storage**: {phone['storage_options']}")
    st.write(f"**Colors**: {phone['colors']}")
    
    if phone['best_2025_flag']:
        st.balloons()
        st.success(f"🎉 {phone['best_2025_flag']}")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
---
<div style='text-align: center; color: #888; padding: 20px;'>
    Made with ❤️ using Streamlit • Data updated Dec 26, 2025<br>
    Samsung Galaxy S25 Ultra = The Ultimate Flagship 👑
</div>
""", unsafe_allow_html=True)