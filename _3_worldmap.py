
from imports import *


def show_worldmap():
    # 1. טעינת נתונים
    df = load_gc()
    if df.empty:
        st.error("No data available.")
        return

    df["date"] = pd.to_datetime(df["date"])

    st.title("🌍 Global Regional Analysis")
    st.caption("Click any continent on the map to update the breakdown chart below.")

    # --- אתחול Session State ---
    if "selected_continent_drilldown" not in st.session_state:
        st.session_state["selected_continent_drilldown"] = "Africa"

    # 2. מיפוי ורשימות (כולל סהרה המערבית)
    input_country_to_continent = {
        'Egypt': 'Africa', 'Nigeria': 'Africa', 'South Africa': 'Africa',
        'Bangladesh': 'Asia', 'China': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia', 'Iraq': 'Asia',
        'Israel': 'Asia',
        'Japan': 'Asia', 'Kazakhstan': 'Asia', 'Malaysia': 'Asia', 'Pakistan': 'Asia', 'Philippines': 'Asia',
        'Qatar': 'Asia', 'Saudi Arabia': 'Asia', 'Singapore': 'Asia', 'South Korea': 'Asia', 'Thailand': 'Asia',
        'Turkey': 'Asia', 'UAE': 'Asia', 'Vietnam': 'Asia',
        'Austria': 'Europe', 'Belgium': 'Europe', 'Czech Republic': 'Europe', 'Denmark': 'Europe',
        'Finland': 'Europe',
        'France': 'Europe', 'Germany': 'Europe', 'Greece': 'Europe', 'Hungary': 'Europe', 'Ireland': 'Europe',
        'Italy': 'Europe', 'Netherlands': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe', 'Romania': 'Europe',
        'Russia': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe', 'United Kingdom': 'Europe',
        'Canada': 'North America', 'Mexico': 'North America', 'United States': 'North America',
        'Argentina': 'South America', 'Brazil': 'South America', 'Chile': 'South America',
        'Colombia': 'South America',
        'Peru': 'South America',
        'Australia': 'Oceania', 'New Zealand': 'Oceania'
    }

    full_continents_lists = {
        'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde',
                   'Central African Republic', 'Chad', 'Comoros', 'Congo', 'Democratic Republic of the Congo',
                   'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia',
                   'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya',
                   'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia',
                   'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
                   'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda',
                   'Zambia',
                   'Zimbabwe', 'Western Sahara'],
        'Asia': ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia',
                 'China', 'Cyprus', 'Georgia', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan',
                 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia',
                 'Myanmar',
                 'Nepal', 'North Korea', 'Oman', 'Pakistan', 'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia',
                 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand',
                 'Timor-Leste',
                 'Turkey', 'Russia', 'Turkmenistan', 'UAE', 'Uzbekistan', 'Vietnam', 'Yemen'],
        'Europe': ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria',
                   'Croatia', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
                   'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania',
                   'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia',
                   'Norway',
                   'Poland', 'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
                   'Sweden',
                   'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican City'],
        'North America': ['Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Canada', 'Costa Rica', 'Cuba',
                          'Dominica', 'Dominican Republic', 'El Salvador', 'Grenada', 'Guatemala', 'Haiti',
                          'Honduras',
                          'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Saint Kitts and Nevis', 'Saint Lucia',
                          'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States'],
        'South America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay',
                          'Peru', 'Suriname', 'Uruguay', 'Venezuela'],
        'Oceania': ['Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'New Zealand',
                    'Palau',
                    'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu']
    }

    df['continent'] = df['country'].map(input_country_to_continent)

    # 3. Controls
    st.markdown("### Controls")
    c1, c2, c3 = st.columns([2.2, 2.0, 2.2])
    with c1:
        metric_label = st.selectbox("Color by metric",
                                    ["Number of events", "Total economic impact (M USD)", "Total injuries",
                                     "Total deaths", "Severity (mean)"], index=1, key="t3_metric")
    with c2:
        allow_norm = metric_label != "Severity (mean)"
        norm_choice = st.radio("Scale", ["Raw", "Normalize (%)"], horizontal=True, disabled=not allow_norm,
                               key="t3_scale")
        normalize = (norm_choice != "Raw") and allow_norm
    with c3:
        min_date, max_date = df["date"].min().to_pydatetime(), df["date"].max().to_pydatetime()
        time_range = st.slider("Time range", min_value=min_date, max_value=max_date,
                               value=st.session_state.get("t3_time_range", (min_date, max_date)), format="YYYY-MM")
        st.session_state["t3_time_range"] = time_range

    # 4. Data Processing
    df_t = df[(df["date"] >= pd.to_datetime(time_range[0])) & (df["date"] <= pd.to_datetime(time_range[1]))].copy()
    if df_t.empty:
        st.warning("No data for selection.")
        return

    # אגרגציה למפה
    metric_map = {"Number of events": "event_type", "Total economic impact (M USD)": "economic_impact_million_usd",
                  "Total injuries": "injuries", "Total deaths": "deaths", "Severity (mean)": "severity"}
    col_name = metric_map[metric_label]

    if metric_label == "Number of events":
        cont_stats = df_t.groupby('continent').size().reset_index(name='value')
    else:
        cont_stats = df_t.groupby('continent')[col_name].agg(
            'mean' if "Severity" in metric_label else 'sum').reset_index(name='value')

    if normalize:
        total_val = cont_stats['value'].sum()
        if total_val > 0: cont_stats['value'] = (cont_stats['value'] / total_val) * 100

    # הרחבה לכל המדינות לצביעה
    plot_rows = []
    for _, row in cont_stats.iterrows():
        if row['continent'] in full_continents_lists:
            for country in full_continents_lists[row['continent']]:
                plot_rows.append({'country': country, 'continent': row['continent'], 'value': row['value']})
    plot_df = pd.DataFrame(plot_rows)

    # 5. הצגת מפה
    color_scale = px.colors.sequential.Reds if "deaths" in metric_label.lower() else px.colors.sequential.Viridis
    fig_map = px.choropleth(
        plot_df, locations="country", locationmode="country names", color="value",
        hover_name="continent", color_continuous_scale=color_scale, projection="natural earth"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=500,
                          geo=dict(showcountries=True, countrycolor="white"))

    # לכידת לחיצה באמצעות point_index (יותר יציב מ-custom_data)
    selection = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")

    if selection and "selection" in selection and selection["selection"]["points"]:
        idx = selection["selection"]["points"][0]["point_index"]
        clicked_cont = plot_df.iloc[idx]["continent"]

        if clicked_cont != st.session_state["selected_continent_drilldown"]:
            st.session_state["selected_continent_drilldown"] = clicked_cont
            st.rerun()

        # 6. Deep Dive (סגנון ישן וחתיך)
        st.divider()
        active_continent = st.session_state["selected_continent_drilldown"]
        st.subheader(f"🔍 Deep Dive: {active_continent}")

        available_conts = sorted(df_t['continent'].dropna().unique())
        if not available_conts:
            st.info("No data for drilldown.")
        else:
            d1, d2 = st.columns([1, 3])
            with d1:
                try:
                    curr_idx = available_conts.index(active_continent)
                except ValueError:
                    curr_idx = 0

                chosen_cont = st.selectbox("Select Continent:", available_conts, index=curr_idx,
                                           key="continent_selector")
                if chosen_cont != active_continent:
                    st.session_state["selected_continent_drilldown"] = chosen_cont
                    st.rerun()

                c_data = df_t[df_t['continent'] == active_continent]

                # הצגת המדדים
                st.metric("Total Events", len(c_data))
                st.metric("Avg Severity", f"{c_data['severity'].mean():.1f}/10")
                # התיקון כאן: שינינו ל-1f.
                st.metric("Total Impact", f"${c_data['economic_impact_million_usd'].sum():,.1f}M")

            with d2:
                if not c_data.empty:
                    # הכנה להיסטוגרמה
                    type_counts = c_data['event_type'].value_counts().reset_index()
                    type_counts.columns = ['Event Type', 'Count']

                    sev_per_type = c_data.groupby('event_type')['severity'].mean().reset_index()
                    type_counts = type_counts.merge(sev_per_type, left_on='Event Type', right_on='event_type')

                    fig_hist = px.bar(
                        type_counts,
                        x='Event Type',
                        y='Count',
                        color='severity',
                        color_continuous_scale='Viridis',
                        text='Count',
                        title=f"Event Distribution in {active_continent}",
                        labels={'severity': 'Avg Severity'},
                        # כאן אנחנו מגדירים את הפורמט של ההובר ל-1 ספרה אחרי הנקודה
                        hover_data={
                            'Event Type': True,
                            'Count': True,
                            'severity': ':.1f'  # ה-f.1 אומר ספרה אחת אחרי הנקודה
                        }
                    )

                    fig_hist.update_traces(textposition='outside')
                    fig_hist.update_layout(height=380, margin=dict(t=40, l=0, r=0, b=0))
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.warning("No data found for this selection.")