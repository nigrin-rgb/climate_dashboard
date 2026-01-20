from imports import *
import plotly.graph_objects as go


def show_analysis():
    # 1. טעינת נתונים
    df = load_gc()
    if df.empty:
        st.error("No data available.")
        return

    st.title("🎛️ Interactive Impact Flow Builder")
    st.markdown("""
    בנה את תרשים הזרימה בעצמך!
    בחר את סוגי האירועים, את המשתנים בדרך, את היעד הסופי, ואת רמת החלוקה (Bins).
    """)

    # --- אזור הבחירה (Sidebar או Top) ---
    st.sidebar.header("⚙️ Flow Settings")

    # A. בחירת סוגי האירועים (המסנן הראשון)
    all_events = sorted(df['event_type'].unique())
    selected_events = st.sidebar.multiselect(
        "1. Filter Event Types",
        all_events,
        default=all_events[:3]  # ברירת מחדל: 3 הראשונים
    )

    if not selected_events:
        st.warning("Please select at least one event type.")
        return

    # סינון הדאטה הראשוני
    dff = df[df['event_type'].isin(selected_events)].copy()

    # B. בחירת המשתנים לזרימה (באמצע)
    # רשימת כל המשתנים הנומריים האפשריים
    numeric_cols = [
        'duration_days', 'affected_population', 'deaths', 'injuries',
        'economic_impact_million_usd', 'infrastructure_damage_score',
        'response_time_hours', 'severity'
    ]

    # שמות יפים לתצוגה
    nice_names = {
        'duration_days': 'Duration',
        'affected_population': 'Affected Pop',
        'deaths': 'Deaths',
        'injuries': 'Injuries',
        'economic_impact_million_usd': 'Economic Cost',
        'infrastructure_damage_score': 'Infra Damage',
        'response_time_hours': 'Response Time',
        'severity': 'Severity'
    }

    selected_dims = st.sidebar.multiselect(
        "2. Choose Intermediate Steps",
        options=numeric_cols,
        format_func=lambda x: nice_names.get(x, x),
        default=['duration_days', 'infrastructure_damage_score']
    )

    # C. בחירת היעד הסופי (Target)
    # נסיר את מה שכבר נבחר באמצע כדי למנוע כפילות, אבל נאפשר למשתמש לבחור כל דבר
    remaining_opts = [c for c in numeric_cols if c not in selected_dims]
    # ברירת מחדל Severity אם לא נבחר כבר
    default_target = 'severity' if 'severity' in remaining_opts else remaining_opts[0] if remaining_opts else None

    target_col = st.sidebar.selectbox(
        "3. Choose Target (End)",
        options=numeric_cols,  # אפשר לבחור הכל, המשתמש מחליט
        index=numeric_cols.index(default_target) if default_target else 0,
        format_func=lambda x: nice_names.get(x, x)
    )

    # D. בחירת רמת החלוקה (N Bins)
    n_bins = st.sidebar.slider(
        "4. Number of Divisions (N)",
        min_value=2, max_value=6, value=4,
        help="2=Low/High, 3=Low/Med/High, 4=Quartiles, etc."
    )

    # --- עיבוד הנתונים ---

    # רשימת כל העמודות לגרף: סוג אירוע -> משתנים נבחרים -> יעד
    # (מוודאים שאין כפילות בין היעד למשתנים באמצע)
    final_dims_cols = []
    if target_col in selected_dims:
        # אם היעד נבחר גם באמצע, נציג אותו רק בסוף
        final_dims_cols = [c for c in selected_dims if c != target_col] + [target_col]
    else:
        final_dims_cols = selected_dims + [target_col]

    # ניקוי שורות ריקות בעמודות הרלוונטיות
    dff = dff.dropna(subset=final_dims_cols).copy()

    # הכנת DataFrame לציור
    plot_df = pd.DataFrame()
    dimensions = []

    # 1. טיפול ב-Event Type (תמיד ראשון)
    # אנחנו רוצים להציג אותו כטקסט
    plot_df['Event Type'] = dff['event_type']
    # מיון לפי שכיחות או א-ב (כאן א-ב כדי שיהיה קבוע)
    event_labels = sorted(dff['event_type'].unique())

    dimensions.append(
        go.parcats.Dimension(
            values=plot_df['Event Type'],
            label='Event Type',
            categoryarray=event_labels
        )
    )

    # 2. לולאה על כל המשתנים הנומריים (כולל היעד)
    for col in final_dims_cols:
        col_label = nice_names.get(col, col)

        # בדיקה מיוחדת: האם זה Severity והמשתמש רוצה את הערכים המקוריים?
        # או באופן כללי: אם יש מעט ערכים ייחודיים (כמו 1-10), לא צריך Binning
        unique_vals = sorted(dff[col].unique())

        if len(unique_vals) <= 12:  # סף שרירותי (מתאים ל-Severity 1-10)
            # משתמשים בערכים המקוריים (Raw)
            plot_df[col_label] = dff[col].astype(int)  # המרה למספר שלם לתצוגה יפה

            dimensions.append(
                go.parcats.Dimension(
                    values=plot_df[col_label],
                    label=col_label,
                    categoryarray=unique_vals,  # סידור נכון (1 למטה, 10 למעלה)
                    ticktext=[str(x) for x in unique_vals]
                )
            )
        else:
            # משתמשים בחלוקה ל-N חלקים (Binning)
            # יצירת תוויות דינמיות (למשל: Tier 1, Tier 2...)
            bin_labels_vals = list(range(n_bins))  # 0, 1, 2...

            # ניסיון ליצור שמות יפים לפי N
            if n_bins == 2:
                bin_text = ['Low', 'High']
            elif n_bins == 3:
                bin_text = ['Low', 'Med', 'High']
            elif n_bins == 4:
                bin_text = ['Q1 (Low)', 'Q2 (Med)', 'Q3 (High)', 'Q4 (Max)']
            elif n_bins == 5:
                bin_text = ['Very Low', 'Low', 'Med', 'High', 'Very High']
            else:
                bin_text = [f'Level {i + 1}' for i in range(n_bins)]

            try:
                plot_df[col_label] = pd.qcut(dff[col], q=n_bins, labels=bin_labels_vals, duplicates='drop')
            except ValueError:
                plot_df[col_label] = pd.cut(dff[col], bins=n_bins, labels=bin_labels_vals)

            # הוספת המימד
            dimensions.append(
                go.parcats.Dimension(
                    values=plot_df[col_label],
                    label=col_label,
                    categoryarray=bin_labels_vals,  # מבטיח סדר עולה
                    ticktext=bin_text
                )
            )

    # --- הציור ---
    # צביעה לפי היעד הסופי (העמודה האחרונה ברשימה)
    # נשתמש בערכים המקוריים של עמודת היעד לצביעה רציפה ויפה
    color_col = final_dims_cols[-1]

    fig = go.Figure(data=[go.Parcats(
        dimensions=dimensions,
        line={
            'color': dff[color_col],  # צביעה לפי הערך המקורי (למשל סכום כסף מדויק)
            'colorscale': 'Viridis',  # או 'Inferno', 'Plasma'
            'shape': 'hspline',
            'showscale': False  # נקי, בלי סרגל
        },
        hoveron='category',
        arrangement='freeform'
    )])

    fig.update_layout(
        height=600,
        margin=dict(l=20, r=20, b=20, t=50),
        title={
            'text': f"Flow Analysis -> Target: {nice_names.get(target_col, target_col)}",
            'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'
        },
        font=dict(size=14)
    )

    st.plotly_chart(fig, use_container_width=True)

    # הצגת הסבר קצר על מה שנבחר
    st.info(f"""
    **Current View:**
    * **Filters:** {', '.join([nice_names.get(c, c) for c in selected_dims])}
    * **Target:** {nice_names.get(target_col, target_col)}
    * **Granularity:** {n_bins} levels (for continuous data)
    """)