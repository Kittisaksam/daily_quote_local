"""Streamlit dashboard for Daily Quote Bot."""
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Daily Quote Bot Dashboard",
    page_icon="🌟",
    layout="wide"
)

# Custom CSS styles
CUSTOM_CSS = """
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
    h1 {
        color: #667eea;
    }
    </style>
"""

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
STATS_FILE = DATA_DIR / "stats.json"
QUOTES_FILE = DATA_DIR / "quotes.json"

# Default stats structure
DEFAULT_STATS = {
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


def load_stats() -> dict:
    """Load statistics from file.

    Returns:
        Statistics dictionary
    """
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_STATS.copy()


def load_quotes() -> list:
    """Load quotes from file.

    Returns:
        List of quote dictionaries
    """
    if QUOTES_FILE.exists():
        with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('quotes', [])
    return []


def format_quote_for_display(quote: dict) -> str:
    """Format a quote for display.

    Args:
        quote: Quote dictionary

    Returns:
        Formatted markdown string
    """
    return f"**{quote['text']}**\n\n— {quote['author']}"


def send_manual_quote() -> bool:
    """Send a quote manually from the dashboard.

    Returns:
        True if successful, False otherwise
    """
    from bot.quote_generator import get_quote
    from bot.telegram_bot import send_quote_sync

    quote = get_quote()
    return send_quote_sync(quote, time_period="manual")


def generate_test_quote() -> str:
    """Generate a test quote for display.

    Returns:
        Formatted quote string
    """
    from bot.quote_generator import get_quote

    quote = get_quote()
    return format_quote_for_display(quote)


def generate_ai_quote(language: str) -> str:
    """Generate an AI quote for display.

    Args:
        language: Language preference

    Returns:
        Formatted quote string
    """
    from bot.quote_generator import get_quote

    quote = get_quote(prefer_ai=True, language=language)
    return format_quote_for_display(quote)


def render_sidebar(stats: dict):
    """Render the sidebar with controls and quick stats.

    Args:
        stats: Statistics dictionary
    """
    with st.sidebar:
        st.header("⚙️ Controls")

        # Manual quote sending
        st.subheader("Send Quote Now")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📤 Send Quote", use_container_width=True):
                if send_manual_quote():
                    st.success("Quote sent successfully!")
                    st.rerun()
                else:
                    st.error("Failed to send quote")

        with col2:
            if st.button("🔄 Test Quote", use_container_width=True):
                st.info(generate_test_quote())

        st.markdown("---")

        # Generate AI quote
        st.subheader("Generate AI Quote")
        language = st.selectbox("Language", ["both", "en", "th"])
        if st.button("🤖 Generate", use_container_width=True):
            with st.spinner("Generating..."):
                st.success(generate_ai_quote(language))

        st.markdown("---")

        # Quick stats
        st.subheader("📊 Quick Stats")
        st.metric("Total Quotes", stats['total_quotes_sent'])
        st.metric("Current Streak", f"{stats['current_streak']} days")
        st.metric("Longest Streak", f"{stats['longest_streak']} days")


def render_metrics(stats: dict):
    """Render top-level metrics.

    Args:
        stats: Statistics dictionary
    """
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


def render_overview_tab(stats: dict):
    """Render overview tab with charts.

    Args:
        stats: Statistics dictionary
    """
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


def render_timeline_tab(stats: dict):
    """Render timeline tab with activity history.

    Args:
        stats: Statistics dictionary
    """
    st.subheader("Quotes Over Time")
    if stats['history']:
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


def render_history_tab(stats: dict):
    """Render quote history tab with filters.

    Args:
        stats: Statistics dictionary
    """
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
                st.markdown(format_quote_for_display(row))
                st.caption(f"Language: {row['language'].upper()} | Source: {row['source']}")
    else:
        st.info("No quote history yet")


def render_quotes_cache_tab(quotes: list):
    """Render local quote cache tab.

    Args:
        quotes: List of cached quotes
    """
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
            st.markdown(format_quote_for_display(quote))
            st.caption(f"Language: {quote.get('language', 'unknown').upper()}")


def main():
    """Main dashboard function."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.title("🌟 Daily Quote Bot Dashboard")
    st.markdown("---")

    # Load data
    stats = load_stats()
    quotes = load_quotes()

    # Render sidebar
    render_sidebar(stats)

    # Render main metrics
    render_metrics(stats)
    st.markdown("---")

    # Render tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🕐 Timeline", "💬 Quote History", "📚 Local Quotes"])

    with tab1:
        render_overview_tab(stats)

    with tab2:
        render_timeline_tab(stats)

    with tab3:
        render_history_tab(stats)

    with tab4:
        render_quotes_cache_tab(quotes)


if __name__ == "__main__":
    main()
