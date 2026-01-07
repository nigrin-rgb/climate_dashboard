# ---------------------------------------------------------
# Task 3 — World Map (Spatial Patterns) with MONTH RANGE slider (bottom)
# ---------------------------------------------------------

from imports import *

def show_worldmap():
    st.title("🗺️ World Map")
    st.caption(
        "Explore where events happen globally. "
        "Filter by event type / severity / encoding, then use the month range slider (bottom) to move through time."
    )

    # -----------------------
    # Load + clean
    # -----------------------
    gc = load_gc()
    df = gc.copy()

    # Ensure numeric
    df["latitude"] = pd.to_numeric(df.get("latitude"), errors="coerce")
    df["longitude"] = pd.to_numeric(df.get("longitude"), errors="coerce")
    df["severity"] = pd.to_numeric(df.get("severity"), errors="coerce")
    df["economic_impact_million_usd"] = pd.to_numeric(df.get("economic_impact_million_usd"), errors="coerce")
    df["year"] = pd.to_numeric(df.get("year"), errors="coerce")
    df["month"] = pd.to_numeric(df.get("month"), errors="coerce")

    # Drop rows without coordinates / time
    df = df.dropna(subset=["latitude", "longitude", "year", "month"]).copy()
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)

    # Remove partial year 2025 (if relevant)
    df = df[df["year"] < 2025].copy()

    # Monthly time key
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1), errors="coerce")
    df = df.dropna(subset=["date"]).copy()

    # Clean event type label for UI/hover
    if "event_type" in df.columns:
        df["event_type_clean"] = (
            df["event_type"].astype(str)
            .str.replace("_", " ", regex=False)
            .str.title()
        )
    else:
        df["event_type_clean"] = "Unknown"

    # -----------------------
    # Filters (NOT time)
    # -----------------------
    st.markdown("### Filters")

    col1, col2, col3, col4 = st.columns([2.2, 2.0, 2.0, 2.2])

    with col1:
        # Show cleaned names in UI, but filter by original values
        if "event_type" in df.columns:
            type_map = (
                df[["event_type", "event_type_clean"]]
                .dropna()
                .drop_duplicates()
                .sort_values("event_type_clean")
            )
            type_labels = type_map["event_type_clean"].tolist()
            label_to_raw = dict(zip(type_map["event_type_clean"], type_map["event_type"]))

            selected_type_labels = st.multiselect(
                "Event types (optional)",
                options=type_labels,
                default=[],
                key="map_event_types",
            )
            selected_types_raw = [label_to_raw[x] for x in selected_type_labels]
        else:
            selected_types_raw = []

    with col2:
        sev_min = float(df["severity"].min()) if df["severity"].notna().any() else 0.0
        sev_max = float(df["severity"].max()) if df["severity"].notna().any() else 10.0
        severity_range = st.slider(
            "Severity range",
            min_value=float(sev_min),
            max_value=float(sev_max),
            value=(float(sev_min), float(sev_max)),
            key="map_severity_range",
        )

    with col3:
        # nicer labels
        color_by_label = st.selectbox(
            "Color by",
            ["Severity", "Event Type", "Economic Impact (M USD)"],
            index=0,
            key="map_color_by",
        )

    with col4:
        size_by_label = st.selectbox(
            "Size by",
            ["Economic Impact (M USD)", "Severity", "None"],
            index=0,
            key="map_size_by",
        )

    # map UI labels -> actual column names
    color_by = {
        "Severity": "severity",
        "Event Type": "event_type_clean",
        "Economic Impact (M USD)": "economic_impact_million_usd",
    }[color_by_label]

    size_by = {
        "Economic Impact (M USD)": "economic_impact_million_usd",
        "Severity": "severity",
        "None": None,
    }[size_by_label]

    # Apply filters (except time)
    df_f = df.copy()

    if selected_types_raw and "event_type" in df_f.columns:
        df_f = df_f[df_f["event_type"].isin(selected_types_raw)].copy()

    if df_f["severity"].notna().any():
        df_f = df_f[df_f["severity"].between(severity_range[0], severity_range[1], inclusive="both")].copy()

    # Safety: if nothing left, stop early
    if df_f.empty:
        st.warning("No data after filters. Try widening filters (event types / severity).")
        return

    # Optional size column (must be non-negative)
    size_col = None
    if size_by is not None and size_by in df_f.columns:
        size_col = size_by
        df_f[size_col] = df_f[size_col].fillna(0).clip(lower=0)

    # -----------------------
    # Quick stats (ALL filtered, before time)
    # -----------------------
    st.markdown("### Quick stats (current filters)")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Events (filtered)", f"{len(df_f):,}")
    with s2:
        st.metric("Countries", f"{df_f['country'].nunique():,}" if "country" in df_f.columns else "n/a")
    with s3:
        st.metric("Date span", f"{df_f['date'].min():%Y-%m} → {df_f['date'].max():%Y-%m}")

    st.write("")

    # -----------------------
    # Default time range = ALL months (so map is NOT empty)
    # Slider will be placed at the BOTTOM, but we need its value now.
    # We'll set it via session_state if not set yet.
    # -----------------------
    min_date = df_f["date"].min()
    max_date = df_f["date"].max()

    if "map_month_range" not in st.session_state:
        st.session_state["map_month_range"] = (min_date.to_pydatetime(), max_date.to_pydatetime())

    start_dt, end_dt = st.session_state["map_month_range"]
    start_dt = pd.to_datetime(start_dt)
    end_dt = pd.to_datetime(end_dt)

    # Filter by the current range (initially: all months)
    df_t = df_f[(df_f["date"] >= start_dt) & (df_f["date"] <= end_dt)].copy()

    # -----------------------
    # MAP
    # -----------------------
    title_range = f"{start_dt:%Y-%m} → {end_dt:%Y-%m}"
    st.subheader(f"World map — {title_range}")

    hover_cols = []
    for c in [
        "year", "month", "country", "event_type_clean", "severity",
        "economic_impact_million_usd", "affected_population", "deaths", "injuries"
    ]:
        if c in df_t.columns:
            hover_cols.append(c)

    fig_map = px.scatter_geo(
        df_t,
        lat="latitude",
        lon="longitude",
        color=color_by if color_by in df_t.columns else None,
        size=size_col if (size_col is not None and size_col in df_t.columns) else None,
        hover_data=hover_cols,
        projection="natural earth",
    )

    fig_map.update_layout(
        template="plotly_dark",
        height=650,
        margin=dict(l=10, r=10, t=50, b=10),
        title="Event locations (after filters + time range)"
    )
    fig_map.update_traces(marker=dict(opacity=0.75))
    st.plotly_chart(fig_map, use_container_width=True)

    # -----------------------
    # TIME SLIDER (BOTTOM) — month RANGE
    # -----------------------
    st.markdown("### Time range (monthly)")

    month_range = st.slider(
        "Choose month range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=st.session_state["map_month_range"],
        format="YYYY-MM",
        key="map_month_range",
        help="Default = full range, so the initial map shows all events."
    )

    # optional: show what’s selected in text
    st.caption(f"Showing events from **{pd.to_datetime(month_range[0]):%Y-%m}** to **{pd.to_datetime(month_range[1]):%Y-%m}**.")