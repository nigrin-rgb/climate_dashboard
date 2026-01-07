from imports import *

def show_severity():
    st.subheader("Distribution: Economic Impact by Severity (Violin + Box)")

    # -----------------------
    # 1) Prepare data
    # -----------------------
    dfv = load_gc()

    # Keep only needed columns (optional but clean)
    needed_cols = ["severity", "economic_impact_million_usd", "year", "country", "event_type"]
    existing = [c for c in needed_cols if c in dfv.columns]
    dfv = dfv[existing].copy()

    # Severity -> integer categories (1..10)
    dfv["severity_int"] = pd.to_numeric(dfv["severity"], errors="coerce").astype("Int64")

    # Economic impact -> numeric, positive only (for log10)
    dfv["economic_impact_million_usd"] = pd.to_numeric(dfv["economic_impact_million_usd"], errors="coerce")
    dfv = dfv.dropna(subset=["severity_int", "economic_impact_million_usd"])
    dfv = dfv[dfv["economic_impact_million_usd"] > 0].copy()

    # log10 transform
    dfv["log10_impact"] = np.log10(dfv["economic_impact_million_usd"])

    # X axis as ordered categories (string labels, but ordered)
    severity_order = sorted(dfv["severity_int"].dropna().unique().tolist())
    dfv["severity_cat"] = dfv["severity_int"].astype(int).astype(str)

    # Optional: clean event type for hover
    if "event_type" in dfv.columns:
        dfv["event_type_clean"] = (
            dfv["event_type"].astype(str)
            .str.replace("_", " ", regex=False)
            .str.title()
        )
    else:
        dfv["event_type_clean"] = "Unknown"

    # -----------------------
    # 2) Build violin figure
    # -----------------------
    fig_v = px.violin(
        dfv,
        x="severity_cat",
        y="log10_impact",
        box=True,
        points=False,
        category_orders={"severity_cat": [str(s) for s in severity_order]},
        labels={
            "severity_cat": "Severity",
            "log10_impact": "log10(Economic Impact in Million USD)"
        },
        title="Economic Impact Distribution by Severity (Violin + Box, log10 scale)",
        # Hover: only show what you want
        hover_data={
            "severity_cat": False,     # already on axis
            "log10_impact": False,     # we'll control via hovertemplate
            "severity_int": True,
            "economic_impact_million_usd": ":.2f",
            "year": True if "year" in dfv.columns else False,
            "country": True if "country" in dfv.columns else False,
            "event_type_clean": True,
        },
    )

    # -----------------------
    # 3) Styling (dark + white faint box)
    # -----------------------
    fig_v.update_layout(
        template="plotly_dark",
        height=650,
        title=dict(font=dict(size=24)),
        font=dict(size=18),
    )

    # Make box white but MORE FADED (you asked: "לבן קצת יותר דהוי")
    # Note: box options apply via update_traces for violin traces.
    fig_v.update_traces(
        box_fillcolor="rgba(255,255,255,0.75)",  # <- change opacity here
        box_line_color="rgba(0,0,0,1)",
        box_line_width=1.5,
        line_color="rgba(126,200,245,0.85)",     # violin outline (subtle)
    )

    fig_v.update_xaxes(title_font=dict(size=25), tickfont=dict(size=20))
    fig_v.update_yaxes(title_font=dict(size=25), tickfont=dict(size=20))

    # -----------------------
    # 4) Hover: show only summary stats (no y, no kde)
    # -----------------------
    fig_v.update_traces(
        hoveron="violins",  # <-- חשוב: בלי "kde"
        hovertemplate=(
            "<b>Severity:</b> %{x}<br>"
            "<b>min:</b> %{min:.2f}<br>"
            "<b>q1:</b> %{q1:.2f}<br>"
            "<b>median:</b> %{median:.2f}<br>"
            "<b>q3:</b> %{q3:.2f}<br>"
            "<b>max:</b> %{max:.2f}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(fig_v, use_container_width=True)