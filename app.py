import streamlit as st

# Import pages (each file exposes a function)
from _1_temporal import show_temporal
from _2_severity import show_severity
from _3_worldmap import show_worldmap

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Climate Events Dashboard",
    page_icon="🌍",
    layout="wide",
)

# -------------------------------------------------
# Sidebar navigation
# -------------------------------------------------
st.sidebar.title("🌍 Climate Events")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "🕒 Temporal Patterns",
        "💥 Severity vs Economic Impact",
        "🗺️ World Map",
    ],
)

# -------------------------------------------------
# Routing
# -------------------------------------------------
if page == "🏠 Overview":
    st.title("🌍 Climate Events Dashboard")

    st.markdown(
        """
        This dashboard explores global climate events using three analytical tasks:

        ### 🕒 Task 1 — Temporal Patterns
        Explore how the **frequency and composition** of climate events change
        over time (yearly / monthly).

        ### 💥 Task 2 — Severity vs Economic Impact
        Analyze the **relationship between event severity and economic damage**,
        identify trends and outliers.

        ### 🗺️ Task 3 — World Map
        Examine the **spatial distribution** of events worldwide, with filters
        for time, event type, severity and impact.

        👉 Use the **sidebar on the left** to navigate between tasks.
        """
    )

elif page == "🕒 Temporal Patterns":
    show_temporal()

elif page == "💥 Severity vs Economic Impact":
    show_severity()

elif page == "🗺️ World Map":
    show_worldmap()