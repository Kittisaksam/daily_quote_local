"""Streamlit dashboard for Daily Quote Bot."""
import json
import logging
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Daily Quote Bot Dashboard",
    page_icon="🌟",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    h1 {
        color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)


def load_stats():
    """Load statistics from file."""
    stats_file = Path(__file__).parent.parent / "data" / "stats.json"
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            'total_quotes_sent': 0,
            'local_quotes_sent': 0,
            'ai_quotes_sent': 0,
            'morning_quotes_sent': 0,
            'evening_quotes_sent': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'last_sent': None,
            'history': []
        }


def load_quotes():
    """Load quotes from file."""
    quotes_file = Path(__file__).parent.parent / "data" / "quotes.json"
    if quotes_file.exists():
        with open(quotes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('quotes', [])
    return []


def main():
    """Main dashboard function."""
    st.title("🌟 Daily Quote Bot Dashboard")
    st.markdown("---")

    # Load data
    stats = load_stats()
    quotes = load_quotes()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")

        # Manual quote sending
        st.subheader("Send Quote Now")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Send Quote", use_container_width=True):
                try:
                    from bot.quote_generator import get_quote
                    from bot.telegram_bot import send_quote_sync

                    quote = get_quote()
                    success = send_quote_sync(quote, time_period="manual")

                    if success:
                        st.success("Quote sent successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to send quote")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            if st.button("🔄 Test Quote", use_container_width=True):
                try:
                    from bot.quote_generator import get_quote

                    quote = get_quote()
                    st.info(f"**Quote:**\n\n{quote['text']}\n\n— {quote['author']}")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")

        # Generate AI quote
        st.subheader("Generate AI Quote")
        language = st.selectbox("Language", ["both", "en", "th"])
        if st.button("🤖 Generate", use_container_width=True):
            try:
                from bot.quote_generator import get_quote

                with st.spinner("Generating..."):
                    quote = get_quote(prefer_ai=True, language=language)
                    st.success(f"**Generated Quote:**\n\n{quote['text']}\n\n— {quote['author']}")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")

        # Stats info
        st.subheader("📊 Quick Stats")
        st.metric("Total Quotes", stats['total_quotes_sent'])
        st.metric("Current Streak", f"{stats['current_streak']} days")
        st.metric("Longest Streak", f"{stats['longest_streak']} days")

    # Main content
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Total Quotes", stats['total_quotes_sent'])

    with col2:
        st.metric("💾 Local", stats['local_quotes_sent'])

    with col3:
        st.metric("🤖 AI Generated", stats['ai_quotes_sent'])

    with col4:
        if stats['last_sent']:
            last_sent = datetime.fromisoformat(stats['last_sent'])
            time_ago = (datetime.now() - last_sent).days
            st.metric("🕐 Last Sent", f"{time_ago} days ago")
        else:
            st.metric("🕐 Last Sent", "Never")

    st.markdown("---")

    # Charts
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🕐 Timeline", "💬 Quote History", "📚 Local Quotes"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Quote Sources")
            if stats['total_quotes_sent'] > 0:
                source_data = {
                    'Source': ['Local', 'AI'],
                    'Count': [stats['local_quotes_sent'], stats['ai_quotes_sent']]
                }
                fig = px.pie(
                    pd.DataFrame(source_data),
                    values='Count',
                    names='Source',
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No quotes sent yet")

        with col2:
            st.subheader("Time Distribution")
            if stats['total_quotes_sent'] > 0:
                time_data = {
                    'Period': ['Morning', 'Evening'],
                    'Count': [stats['morning_quotes_sent'], stats['evening_quotes_sent']]
                }
                fig = px.bar(
                    pd.DataFrame(time_data),
                    x='Period',
                    y='Count',
                    color='Period',
                    color_discrete_map={'Morning': '#f6ad55', 'Evening': '#4299e1'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No quotes sent yet")

        # Streak info
        st.subheader("🔥 Streak Information")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Streak", f"{stats['current_streak']} days")
        with col2:
            st.metric("Longest Streak", f"{stats['longest_streak']} days")

    with tab2:
        st.subheader("Quotes Over Time")
        if stats['history']:
            # Convert history to DataFrame
            df = pd.DataFrame(stats['history'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date

            # Group by date
            daily_counts = df.groupby('date').size().reset_index(name='count')

            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title='Quotes Sent per Day',
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Quotes"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Recent activity
            st.subheader("Recent Activity")
            recent = df.tail(10)[::-1]  # Last 10, reversed
            for _, row in recent.iterrows():
                timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                source_emoji = "🤖" if row['source'] == 'ai' else "💾"
                time_emoji = "🌅" if row['time_period'] == 'morning' else "🌆"
                st.markdown(f"{source_emoji} {time_emoji} **{timestamp}**\n> {row['text'][:80]}...")
        else:
            st.info("No quote history yet")

    with tab3:
        st.subheader("Quote History")
        if stats['history']:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                source_filter = st.selectbox("Filter by Source", ["All", "local", "ai"])
            with col2:
                lang_filter = st.selectbox("Filter by Language", ["All", "en", "th"])
            with col3:
                period_filter = st.selectbox("Filter by Time", ["All", "morning", "evening"])

            # Apply filters
            df = pd.DataFrame(stats['history'])
            if source_filter != "All":
                df = df[df['source'] == source_filter]
            if lang_filter != "All":
                df = df[df['language'] == lang_filter]
            if period_filter != "All":
                df = df[df['time_period'] == period_filter]

            # Display
            for _, row in df[::-1].iterrows():
                timestamp = datetime.fromisoformat(row['timestamp']).strftime('%Y-%m-%d %H:%M')
                source_emoji = "🤖" if row['source'] == 'ai' else "💾"
                time_emoji = "🌅" if row['time_period'] == 'morning' else "🌆"

                with st.expander(f"{source_emoji} {time_emoji} {timestamp} - {row['text'][:50]}..."):
                    st.markdown(f"**{row['text']}**\n\n— {row['author']}")
                    st.caption(f"Language: {row['language'].upper()} | Source: {row['source']}")
        else:
            st.info("No quote history yet")

    with tab4:
        st.subheader("Local Quote Cache")
        st.info(f"Total quotes in cache: {len(quotes)}")

        # Language filter
        lang_filter = st.selectbox("Filter by Language", ["All", "en", "th"], key="cache_filter")

        filtered_quotes = quotes
        if lang_filter != "All":
            filtered_quotes = [q for q in quotes if q.get('language') == lang_filter]

        # Display quotes
        for quote in filtered_quotes:
            lang_emoji = "🇬🇧" if quote.get('language') == 'en' else "🇹🇭"
            with st.expander(f"{lang_emoji} {quote['text'][:50]}..."):
                st.markdown(f"**{quote['text']}**\n\n— {quote['author']}")
                st.caption(f"Language: {quote.get('language', 'unknown').upper()}")


if __name__ == "__main__":
    main()
