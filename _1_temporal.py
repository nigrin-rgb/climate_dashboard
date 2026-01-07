from imports import *  # assumes: st, pd, np, px, calendar, load_gc

def show_temporal():
    gc = load_gc()

    st.title("🌪️ Temporal Patterns (2020–2024)")
    st.caption("Comparison mode: grouped bars (side-by-side) with Event types / Categories + Random 4.")
    st.write("")

    # ---------------------------------------------------------
    # Comparison mode (Plotly)
    # ---------------------------------------------------------
    st.subheader("Comparison mode: grouped bars (side-by-side)")

    # ====== 1) Define your categories (exactly as requested) ======
    CATEGORY_MAP = {
        "Geophysical": ["earthquake", "volcanic eruption", "tsunami"],
        "Geomorphological": ["landslide"],
        "Atmospheric": ["hailstorm", "tornado", "hurricane"],
        "Climatological": ["coldwave", "heatwave", "drought"],
        "Hydrological": ["flood"],
        "Ecological": ["wildfire"],
    }

    # Normalize strings for matching: lower + strip + underscores->space
    def _norm(s: str) -> str:
        return str(s).strip().lower().replace("_", " ")

    # All event types in data (raw)
    all_event_types_raw = sorted(gc["event_type"].dropna().astype(str).unique().tolist())
    # Normalized lookup: norm -> original
    norm_to_raw = { _norm(x): x for x in all_event_types_raw }

    # For categories: keep only events that actually exist in the dataset
    category_to_existing_raw = {}
    for cat, evs in CATEGORY_MAP.items():
        existing = []
        for e in evs:
            key = _norm(e)
            if key in norm_to_raw:
                existing.append(norm_to_raw[key])
        category_to_existing_raw[cat] = existing

    # Build labels: "Category (A, B, C)"
    def pretty_event_label(raw_event_type: str) -> str:
        # "volcanic_eruption" -> "Volcanic eruption"
        return str(raw_event_type).replace("_", " ").strip().title()

    category_labels = []
    label_to_category = {}
    for cat, raw_events in category_to_existing_raw.items():
        inside = ", ".join([pretty_event_label(x) for x in raw_events]) if raw_events else "No matching events in data"
        label = f"{cat} ({inside})"
        category_labels.append(label)
        label_to_category[label] = cat

    st.markdown("""
    <style>
  
    div[data-testid="stHorizontalBlock"]{
        align-items: flex-start !important;
        gap: 48px !important;             
    }

    
    div[data-testid="column"]{
        padding-right: 8px !important;
    }


    div[data-testid="stRadio"] > label{
        margin-bottom: 4px !important;
    }
    div[data-testid="stRadio"] label{
        padding: 0 !important;
        margin: 0 !important;
    }

 
    div[data-testid="stRadio"] div[role="radiogroup"]{
        gap: 18px !important;         
    }


    .ctrl-title{
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        opacity: 0.95 !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # ====== 2) Top control bar (keep the same look) ======
    c1, c2, c3, c4 = st.columns([1.4, 2.2, 1.8, 1.6])

    with c1:
        st.markdown('<p class="ctrl-title">Time unit</p>', unsafe_allow_html=True)
        time_unit = st.radio(
            "Time unit",
            ["Year", "Month"],
            horizontal=True,
            label_visibility="collapsed",
            key="cmp_time_unit"
        )

    with c2:
        st.markdown('<p class="ctrl-title">Pick by</p>', unsafe_allow_html=True)
        pick_by = st.radio(
            "Pick by",
            ["Event types", "Categories"],
            horizontal=True,
            label_visibility="collapsed",
            key="cmp_pick_by"
        )

    with c3:
        st.markdown('<p class="ctrl-title">Scale</p>', unsafe_allow_html=True)
        scale_mode = st.radio(
            "Scale",
            ["Count", "Normalize (%)"],
            horizontal=True,
            label_visibility="collapsed",
            key="cmp_scale_mode"
        )

    with c4:
        st.markdown('<p class="ctrl-title">&nbsp;</p>', unsafe_allow_html=True)  # “כותרת” ריקה כדי לשמור גובה זהה
        random_clicked = st.button("🎲 Random 3", use_container_width=True, key="cmp_random3")

    normalize = (scale_mode == "Normalize (%)")
    # ====== 3) Selection state (Random 4 that actually works) ======
    # Keys for widget states:
    KEY_TYPES = "cmp_selected_event_types"
    KEY_CATS = "cmp_selected_categories"

    # Init defaults (first time only)
    if KEY_TYPES not in st.session_state:
        st.session_state[KEY_TYPES] = (
            all_event_types_raw if len(all_event_types_raw) <= 3
            else list(np.random.choice(all_event_types_raw, size=3, replace=False))
        )
    if KEY_CATS not in st.session_state:
        st.session_state[KEY_CATS] = (
            category_labels if len(category_labels) <= 3
            else list(np.random.choice(category_labels, size=3, replace=False))
        )

    # Random button logic
    if random_clicked:
        if pick_by == "Event types":
            st.session_state[KEY_TYPES] = (
                all_event_types_raw if len(all_event_types_raw) <= 3
                else list(np.random.choice(all_event_types_raw, size=3, replace=False))
            )
        else:
            st.session_state[KEY_CATS] = (
                category_labels if len(category_labels) <= 3
                else list(np.random.choice(category_labels, size=3, replace=False))
            )
        st.rerun()

    # ====== 4) The picker itself (aligned on one line, clean) ======
    if pick_by == "Event types":
        selected_event_types = st.multiselect(
            "Choose event types to compare",
            options=all_event_types_raw,
            key=KEY_TYPES
        )
        chosen_event_types_raw = selected_event_types

        if len(chosen_event_types_raw) == 0:
            st.warning("Pick at least one event type.")
            st.stop()

        # For plot legend: clean labels
        legend_map = {e: pretty_event_label(e) for e in chosen_event_types_raw}

    else:
        selected_categories = st.multiselect(
            "Choose categories to compare",
            options=category_labels,
            key=KEY_CATS
        )

        if len(selected_categories) == 0:
            st.warning("Pick at least one category.")
            st.stop()

        # Convert categories -> list of event types
        chosen_event_types_raw = []
        cat_for_event = {}
        for label in selected_categories:
            cat = label_to_category[label]
            for e in category_to_existing_raw.get(cat, []):
                chosen_event_types_raw.append(e)
                cat_for_event[e] = cat

        chosen_event_types_raw = sorted(list(set(chosen_event_types_raw)))

        if len(chosen_event_types_raw) == 0:
            st.warning("Selected categories contain no matching events in the dataset.")
            st.stop()

        # Legend should be categories, not event types
        legend_map = {}  # handled later

    st.write("")

    # ====== 5) For Month mode, pick a year (to avoid mixing years) ======
    years_all = sorted(gc["year"].dropna().astype(int).unique().tolist())
    chosen_year_for_month = None

    if time_unit == "Month":
        chosen_year_for_month = st.selectbox(
            "Year (for monthly comparison)",
            years_all,
            index=len(years_all)-1 if years_all else 0,
            key="cmp_month_year"
        )

    # ====== 6) Prepare filtered data ======
    df = gc.copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["month"] = pd.to_numeric(df["month"], errors="coerce")
    df = df.dropna(subset=["year", "month", "event_type"]).copy()
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)

    # Filter by chosen event types
    df = df[df["event_type"].isin(chosen_event_types_raw)].copy()

    # Define time axis
    if time_unit == "Year":
        x_col = "year"
        x_order = sorted(df["year"].unique().tolist())
        x_labels = [str(x) for x in x_order]
    else:
        df = df[df["year"] == int(chosen_year_for_month)].copy()
        x_col = "month"
        x_order = list(range(1, 13))
        x_labels = [calendar.month_abbr[m] for m in x_order]

    # ====== 7) Aggregate to pivot ======
    if pick_by == "Event types":
        counts = (
            df.groupby([x_col, "event_type"])
              .size()
              .reset_index(name="count")
        )
        pivot = counts.pivot(index=x_col, columns="event_type", values="count").fillna(0)
        pivot = pivot.reindex(x_order, fill_value=0)

        if normalize:
            row_sums = pivot.sum(axis=1).replace(0, np.nan)
            pivot = (pivot.div(row_sums, axis=0) * 100).fillna(0)

        # Rename columns for legend
        pivot = pivot.rename(columns=legend_map)

    else:
        # Category mode: sum counts of events within each category
        df["category"] = df["event_type"].map(cat_for_event)

        counts = (
            df.groupby([x_col, "category"])
              .size()
              .reset_index(name="count")
        )
        pivot = counts.pivot(index=x_col, columns="category", values="count").fillna(0)
        pivot = pivot.reindex(x_order, fill_value=0)

        if normalize:
            row_sums = pivot.sum(axis=1).replace(0, np.nan)
            pivot = (pivot.div(row_sums, axis=0) * 100).fillna(0)

        # Make category labels nicer
        pivot.columns = [str(c).title() for c in pivot.columns]

    # Convert pivot to long format for Plotly grouped bars
    plot_df = pivot.reset_index().melt(id_vars=[x_col], var_name="Series", value_name="Value")

    # Ensure x is categorical to preserve order
    plot_df[x_col] = pd.Categorical(plot_df[x_col], categories=x_order, ordered=True)

    # ====== 8) Plotly grouped bar chart ======
    y_title = "Percent (%)" if normalize else "Count"
    if time_unit == "Month":
        title = f"Grouped comparison by month — {chosen_year_for_month}" + (" (normalized)" if normalize else "")
        x_title = "Month"
    else:
        title = "Grouped comparison by year" + (" (normalized)" if normalize else "")
        x_title = "Year"

    fig = px.bar(
        plot_df,
        x=x_col,
        y="Value",
        color="Series",
        barmode="group",
        labels={x_col: x_title, "Value": y_title, "Series": "Event Type" if pick_by == "Event types" else "Category"},
        title=title,
    )

    fig.update_layout(
        template="plotly_dark",
        height=520,
        title=dict(text=title, x=0, xanchor="left", y=0.97, yanchor="top", font=dict(size=22)),
        font=dict(size=16),

        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title_text="Event Type",
            bgcolor="rgba(0,0,0,0)",
        ),

        margin=dict(l=20, r=160, t=80, b=40),
    )

    # Fix tick labels (years as 2022, not 2,022)
    if time_unit == "Year":
        fig.update_xaxes(
            tickmode="array",
            tickvals=x_order,
            ticktext=[str(y) for y in x_order],
        )
    else:
        fig.update_xaxes(
            tickmode="array",
            tickvals=x_order,
            ticktext=x_labels,
        )

    fig.update_yaxes(title_font=dict(size=18), tickfont=dict(size=14))
    fig.update_xaxes(title_font=dict(size=18), tickfont=dict(size=14))

    st.plotly_chart(fig, use_container_width=True)

    # Small hint
    st.caption("Tip: switch to Categories to reduce clutter; use Normalize (%) to compare composition instead of raw volume.")