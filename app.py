import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="SDG 4 Dashboard", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── Base ─────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a2340;
}

.main { background-color: #f0f3f9; }

h1, h2, h3, h4 {
    font-family: 'DM Serif Display', serif;
    color: #1a2340;
}

/* ── Page title ───────────────────────────────────────── */
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #1a2340;
    margin-bottom: 2px;
}

.page-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #5a6a8a;
    margin-bottom: 24px;
    font-weight: 400;
}

/* ── Section headers ──────────────────────────────────── */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.45rem;
    color: #1a2340;
    margin: 28px 0 14px 0;
    border-left: 4px solid #3B60E4;
    padding-left: 12px;
}

/* ── KPI Cards ────────────────────────────────────────── */
.kpi-card {
    padding: 20px 14px 18px 14px;
    border-radius: 16px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0,0,0,0.13);
    margin-bottom: 12px;
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); }

.kpi-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.88;
    margin-bottom: 6px;
    color: #ffffff;
}

.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.85rem;
    font-weight: 400;
    color: #ffffff;
    line-height: 1.1;
}

/* ── Insight boxes ────────────────────────────────────── */
.insight-blue {
    padding: 20px 22px;
    border-radius: 14px;
    background: #EEF3FF;
    border-left: 5px solid #3B60E4;
    margin: 14px 0 20px 0;
    box-shadow: 0 2px 10px rgba(59,96,228,0.09);
}

.insight-teal {
    padding: 20px 22px;
    border-radius: 14px;
    background: #EDFAF5;
    border-left: 5px solid #10B981;
    margin: 14px 0 20px 0;
    box-shadow: 0 2px 10px rgba(16,185,129,0.09);
}

.insight-violet {
    padding: 20px 22px;
    border-radius: 14px;
    background: #F3EEFF;
    border-left: 5px solid #7C3AED;
    margin: 14px 0 20px 0;
    box-shadow: 0 2px 10px rgba(124,58,237,0.09);
}

.insight-amber {
    padding: 20px 22px;
    border-radius: 14px;
    background: #FFFBEE;
    border-left: 5px solid #F59E0B;
    margin: 14px 0 20px 0;
    box-shadow: 0 2px 10px rgba(245,158,11,0.09);
}

/* shared text rules for all insight boxes */
.insight-blue h4,
.insight-teal h4,
.insight-violet h4,
.insight-amber h4 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.05rem;
    color: #1a2340;
    margin: 0 0 10px 0;
}

.insight-blue p,
.insight-teal p,
.insight-violet p,
.insight-amber p,
.insight-blue span,
.insight-teal span,
.insight-violet span,
.insight-amber span {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.93rem;
    color: #2e3d5c;
    line-height: 1.65;
    margin: 0;
}

.insight-blue strong,
.insight-teal strong,
.insight-violet strong,
.insight-amber strong {
    color: #1a2340;
    font-weight: 600;
}

/* ── Regression table title ───────────────────────────── */
.reg-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.35rem;
    color: #1a2340;
    margin: 18px 0 10px 0;
}

/* ── Interpretation cards ─────────────────────────────── */
.interp-card {
    padding: 18px 22px;
    border-radius: 14px;
    background: #ffffff;
    border-left: 5px solid #3B60E4;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}

.interp-card h4 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.0rem;
    color: #1a2340;
    margin: 0 0 8px 0;
}

.interp-card p {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.91rem;
    color: #2e3d5c;
    line-height: 1.65;
    margin: 0;
}

.interp-card strong {
    color: #1a2340;
    font-weight: 600;
}

/* interp accent colors */
.interp-pos { border-left-color: #10B981; }
.interp-neg { border-left-color: #EF4444; }

/* ── Divider ──────────────────────────────────────────── */
.divider {
    border: none;
    border-top: 1.5px solid #dde3f0;
    margin: 28px 0;
}

/* ── Dataframe tweaks ─────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}

</style>
""", unsafe_allow_html=True)

# ── TITLE ────────────────────────────────────────────────────────────────────

st.markdown('<p class="page-title">🎓 SDG 4: Drivers of Tertiary Enrollment</p>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Investigating socio-economic factors affecting tertiary school enrollment across countries</p>', unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_tertiary_enrollment_data.csv")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    required_columns = [
        'Country Name', 'Country Code', 'Tertiary_Enrollment',
        'Gov_Expenditure_Education', 'Internet_Usage', 'GDP_per_Capita',
        'Upper_Secondary_Completion', 'Urban_Population'
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = np.nan
    df['GDP_per_Capita_Log'] = np.log1p(df['GDP_per_Capita'])
    return df

df = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

st.sidebar.header("Dashboard Controls")

selected_year = st.sidebar.slider(
    "Select Year",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=int(df['Year'].max())
)

country_options = ['All'] + sorted(df['Country Name'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_options)

driver_options = {
    'Government Expenditure (% GDP)': 'Gov_Expenditure_Education',
    'Internet Usage (% Population)':  'Internet_Usage',
    'Log GDP per Capita':              'GDP_per_Capita_Log',
    'Upper Secondary Completion':      'Upper_Secondary_Completion',
    'Urban Population (%)':            'Urban_Population'
}

selected_driver_label = st.sidebar.selectbox(
    "Choose Explanatory Driver", list(driver_options.keys())
)
selected_driver = driver_options[selected_driver_label]

filtered_df = df[df['Year'] == selected_year]

# ── KPI SECTION ──────────────────────────────────────────────────────────────

st.markdown('<p class="section-header">📊 Global KPI Indicators</p>', unsafe_allow_html=True)

tertiary = filtered_df['Tertiary_Enrollment'].mean()
internet = filtered_df['Internet_Usage'].mean()
gov      = filtered_df['Gov_Expenditure_Education'].mean()
gdp      = filtered_df['GDP_per_Capita'].mean()
upper    = filtered_df['Upper_Secondary_Completion'].mean()
urban    = filtered_df['Urban_Population'].mean()

kpi_data = [
    ("#1E3A8A", "Enrollment",       f"{tertiary:.1f}%"),
    ("#2563EB", "Internet Access",  f"{internet:.1f}%"),
    ("#059669", "Edu. Spending",    f"{gov:.1f}%"),
    ("#7C3AED", "GDP per Capita",   f"${gdp:,.0f}"),
    ("#D97706", "Upper Secondary",  f"{upper:.1f}%"),
    ("#DC2626", "Urban Population", f"{urban:.1f}%"),
]

cols = st.columns(6)
for col, (color, label, value) in zip(cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="background:{color};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── MAP + SCATTER ─────────────────────────────────────────────────────────────

map_col, scatter_col = st.columns(2)

# — Choropleth Map —
with map_col:
    st.markdown('<p class="section-header">🌍 Global Enrollment Map</p>', unsafe_allow_html=True)

    map_df = filtered_df.dropna(subset=['Country Code', 'Tertiary_Enrollment'])

    map_fig = px.choropleth(
        map_df,
        locations='Country Code',
        color='Tertiary_Enrollment',
        hover_name='Country Name',
        color_continuous_scale='Blues',
        title=f"Tertiary Enrollment Rate ({selected_year})"
    )
    map_fig.update_layout(
        template='plotly_white',
        height=460,
        font=dict(family='DM Sans', color='#1a2340'),
        title_font=dict(family='DM Serif Display', size=16, color='#1a2340'),
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(map_fig, use_container_width=True)

    if not map_df.empty:
        top    = map_df.loc[map_df['Tertiary_Enrollment'].idxmax()]
        bottom = map_df.loc[map_df['Tertiary_Enrollment'].idxmin()]
        st.markdown(f"""
        <div class="insight-blue">
            <h4>🌍 Geographic Enrollment Insights</h4>
            <p>
            The map shows tertiary enrollment distribution for <strong>{selected_year}</strong>.
            <br><br>
            <strong>{top['Country Name']}</strong> leads with <strong>{top['Tertiary_Enrollment']:.1f}%</strong> enrollment —
            reflecting strong higher-education accessibility.
            <br><br>
            <strong>{bottom['Country Name']}</strong> recorded the lowest at <strong>{bottom['Tertiary_Enrollment']:.1f}%</strong>,
            highlighting persistent access barriers in some regions.
            </p>
        </div>""", unsafe_allow_html=True)

# — Scatter —
with scatter_col:
    st.markdown(f'<p class="section-header">📈 Enrollment vs {selected_driver_label}</p>', unsafe_allow_html=True)

    scatter_df = filtered_df.dropna(subset=['Tertiary_Enrollment', selected_driver])
    trendline_mode = "ols" if len(scatter_df) > 1 else None

    scatter_fig = px.scatter(
        scatter_df,
        x=selected_driver,
        y='Tertiary_Enrollment',
        hover_name='Country Name',
        trendline=trendline_mode,
        labels={selected_driver: selected_driver_label, 'Tertiary_Enrollment': 'Enrollment (%)'},
        color_discrete_sequence=['#3B60E4']
    )

    if selected_country != 'All':
        c_df = scatter_df[scatter_df['Country Name'] == selected_country]
        if not c_df.empty:
            scatter_fig.add_trace(go.Scatter(
                x=c_df[selected_driver],
                y=c_df['Tertiary_Enrollment'],
                mode='markers',
                marker=dict(color='#EF4444', size=14, symbol='diamond',
                            line=dict(color='white', width=2)),
                name=selected_country
            ))

    scatter_fig.update_layout(
        template='plotly_white',
        height=460,
        font=dict(family='DM Sans', color='#1a2340'),
        title_font=dict(family='DM Serif Display', size=16, color='#1a2340'),
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,250,255,1)',
        legend=dict(font=dict(family='DM Sans', color='#1a2340'))
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    corr = scatter_df[[selected_driver, 'Tertiary_Enrollment']].corr().iloc[0, 1]
    direction = "positive" if corr > 0 else "negative"
    strength  = "strong" if abs(corr) >= 0.7 else "moderate" if abs(corr) >= 0.4 else "weak"

    st.markdown(f"""
    <div class="insight-teal">
        <h4>📊 Driver Relationship Insights</h4>
        <p>
        There is a <strong>{strength} {direction} relationship</strong> between
        <strong>{selected_driver_label}</strong> and tertiary enrollment in <strong>{selected_year}</strong>.
        <br><br>
        Countries with higher <strong>{selected_driver_label}</strong> generally show
        {"higher" if corr > 0 else "lower"} enrollment rates.
        <br><br>
        Pearson Correlation: <strong>{corr:.3f}</strong>
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── HISTORICAL TREND ──────────────────────────────────────────────────────────

st.markdown('<p class="section-header">📉 Historical Enrollment Trend</p>', unsafe_allow_html=True)

if selected_country == 'All':
    trend_df    = df.groupby('Year')['Tertiary_Enrollment'].mean().reset_index()
    trend_title = "Global Mean Tertiary Enrollment Over Time"
else:
    trend_df    = df[df['Country Name'] == selected_country]
    trend_title = f"Enrollment Trend — {selected_country}"

trend_fig = px.line(
    trend_df, x='Year', y='Tertiary_Enrollment',
    markers=True, title=trend_title,
    color_discrete_sequence=['#3B60E4']
)
trend_fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
trend_fig.update_layout(
    template='plotly_white',
    height=420,
    font=dict(family='DM Sans', color='#1a2340'),
    title_font=dict(family='DM Serif Display', size=17, color='#1a2340'),
    yaxis_range=[0, 110],
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(248,250,255,1)',
    margin=dict(l=0, r=0, t=40, b=0)
)
st.plotly_chart(trend_fig, use_container_width=True)

if len(trend_df) > 1:
    start_val = trend_df['Tertiary_Enrollment'].iloc[0]
    end_val   = trend_df['Tertiary_Enrollment'].iloc[-1]
    change    = end_val - start_val
    direction = "increased" if change > 0 else "decreased"
    tone      = "improvement" if change > 0 else "decline"

    st.markdown(f"""
    <div class="insight-violet">
        <h4>📉 Historical Trend Insights</h4>
        <p>
        Tertiary enrollment has <strong>{direction}</strong> from
        <strong>{start_val:.1f}%</strong> to <strong>{end_val:.1f}%</strong>
        over the observed period — an overall {tone} of
        <strong>{abs(change):.1f} percentage points</strong> in tertiary education participation.
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── MULTIPLE REGRESSION ───────────────────────────────────────────────────────

st.markdown('<p class="section-header">🔬 Multiple Regression Analysis</p>', unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'DM Sans\',sans-serif;font-size:0.95rem;color:#5a6a8a;margin-bottom:18px;">'
    'This model estimates how socio-economic indicators jointly affect tertiary enrollment across countries.</p>',
    unsafe_allow_html=True
)

regression_features = [
    'Gov_Expenditure_Education', 'Internet_Usage', 'GDP_per_Capita_Log',
    'Upper_Secondary_Completion', 'Urban_Population'
]

reg_df = filtered_df[['Tertiary_Enrollment'] + regression_features].copy()
for col in reg_df.columns:
    reg_df[col] = pd.to_numeric(reg_df[col], errors='coerce')
reg_df = reg_df.dropna()

if len(reg_df) > 10:
    X = sm.add_constant(reg_df[regression_features])
    y = reg_df['Tertiary_Enrollment']
    model = sm.OLS(y, X).fit()

    rename_map = {
        'Gov_Expenditure_Education': 'Education Spending',
        'Internet_Usage':            'Internet Access',
        'GDP_per_Capita_Log':        'GDP per Capita (Log)',
        'Upper_Secondary_Completion':'Upper Secondary Completion',
        'Urban_Population':          'Urban Population'
    }

    regression_table = pd.DataFrame({
        'Explanatory Variable': [rename_map[v] for v in regression_features],
        'Coefficient':          model.params.drop('const').values,
        'Std Error':            model.bse.drop('const').values,
        'T-Statistic':          model.tvalues.drop('const').values,
        'P-Value':              model.pvalues.drop('const').values,
        'Relationship':         ['Positive' if c > 0 else 'Negative'
                                 for c in model.params.drop('const').values]
    })

    st.markdown('<p class="reg-title">📋 Regression Results</p>', unsafe_allow_html=True)

    st.dataframe(
        regression_table.style
            .format({'Coefficient': '{:.3f}', 'Std Error': '{:.3f}',
                     'T-Statistic': '{:.3f}', 'P-Value': '{:.4f}'})
            .applymap(
                lambda v: 'color:#059669;font-weight:600' if v == 'Positive'
                          else 'color:#DC2626;font-weight:600',
                subset=['Relationship']
            )
            .applymap(
                lambda v: 'color:#059669;font-weight:600' if isinstance(v, float) and v < 0.05
                          else 'color:#5a6a8a',
                subset=['P-Value']
            ),
        use_container_width=True,
        hide_index=True
    )

    r_squared = model.rsquared
    st.markdown(f"""
    <div class="insight-amber">
        <h4>🧠 Overall Model Performance</h4>
        <p>
        The regression model achieved an <strong>R² of {r_squared:.3f}</strong>, meaning approximately
        <strong>{r_squared*100:.1f}%</strong> of the variation in tertiary enrollment is explained
        by the five socio-economic variables included in the model.
        </p>
    </div>""", unsafe_allow_html=True)

    # — Variable Interpretations —
    st.markdown('<p class="section-header">📘 Variable Interpretation</p>', unsafe_allow_html=True)

    accent_colors = {
        'Education Spending':          '#2563EB',
        'Internet Access':             '#059669',
        'GDP per Capita (Log)':        '#7C3AED',
        'Upper Secondary Completion':  '#D97706',
        'Urban Population':            '#DC2626',
    }

    for _, row in regression_table.iterrows():
        variable = row['Explanatory Variable']
        coef     = row['Coefficient']
        pval     = row['P-Value']
        relation = row['Relationship']
        color    = accent_colors.get(variable, '#3B60E4')

        strength = (
            "strong" if abs(coef) >= 1 else
            "moderate" if abs(coef) >= 0.3 else
            "weak"
        )
        significance = (
            "statistically significant" if pval < 0.05
            else "not statistically significant"
        )
        pos_neg = "increase" if coef > 0 else "decrease"

        st.markdown(f"""
        <div class="interp-card {'interp-pos' if coef > 0 else 'interp-neg'}"
             style="border-left-color:{color};">
            <h4>{variable}</h4>
            <p>
            A one-unit increase in <strong>{variable}</strong> is associated with an estimated
            <strong>{abs(coef):.3f}-point {pos_neg}</strong> in tertiary enrollment for
            <strong>{selected_year}</strong>. This variable shows a
            <strong>{strength} {relation.lower()} relationship</strong> and is
            <strong>{significance}</strong> at conventional levels (p = {pval:.4f}).
            </p>
        </div>""", unsafe_allow_html=True)

else:
    st.warning("Insufficient data for regression analysis in the selected year.")
