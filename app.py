import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── PAGE CONFIG 

st.set_page_config(page_title="SDG 4 Dashboard", layout="wide")

st.markdown("""
<style>
/* Base */
.main { background-color: var(--background-color); }

/* KPI Cards */
.kpi-card {
    padding: 24px 16px;
    border-radius: 12px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 16px;
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform: translateY(-4px); }

.kpi-label {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    opacity: 0.9;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 2.2rem;
    font-weight: 600;
    line-height: 1.1;
}

/* Insight boxes */
.insight-box {
    padding: 24px;
    border-radius: 12px;
    margin: 16px 0 24px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.insight-box.blue   { background-color: #172554; border-left: 6px solid #3B82F6; } /* Deep Navy */
.insight-box.teal   { background-color: #022C22; border-left: 6px solid #10B981; } /* Forest Teal */
.insight-box.violet { background-color: #2E1065; border-left: 6px solid #8B5CF6; } /* Midnight Violet */
.insight-box.amber  { background-color: #451A03; border-left: 6px solid #F59E0B; } /* Dark Amber */

.insight-box h4 {
    font-size: 1.25rem;
    margin: 0 0 12px 0;
    color: #F8FAFC; 
}

.insight-box p, .insight-box span {
    font-size: 1.05rem;
    line-height: 1.6;
    margin: 0;
    color: #E2E8F0;
}

.insight-box strong {
    font-weight: 700;
    color: #FFFFFF;
}

/* Regression table title */
.reg-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 24px 0 12px 0;
}

/* Interpretation cards */
.interp-card {
    padding: 22px;
    border-radius: 12px;
    background-color: #0F172A; 
    border: 1px solid #1E293B;
    margin-bottom: 16px;
    height: 90%;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.interp-card h4 {
    font-size: 1.15rem;
    margin: 0 0 10px 0;
    color: #F8FAFC;
    border-bottom: 2px solid #38BDF8;
    display: inline-block;
    padding-bottom: 4px;
}

.interp-card p {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0;
    color: #CBD5E1; 
}

.interp-card strong {
    color: #FFFFFF;
}

/* Divider */
.divider {
    border: none;
    border-top: 2px solid var;
    margin: 32px 0;
}

/* Dataframe tweaks */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# TITLE 

st.title("🎓 SDG 4: Drivers of Tertiary Enrollment")
st.write("Investigating socio-economic factors affecting tertiary school enrollment across countries")

# LOAD DATA 

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

# SIDEBAR 

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
    'Log GDP per Capita':             'GDP_per_Capita_Log',
    'Upper Secondary Completion':     'Upper_Secondary_Completion',
    'Urban Population (%)':           'Urban_Population'
}

selected_driver_label = st.sidebar.selectbox(
    "Choose Explanatory Driver", list(driver_options.keys())
)
selected_driver = driver_options[selected_driver_label]

filtered_df = df[df['Year'] == selected_year]

# KPI SECTION 

st.subheader("📊 Global KPI Indicators")

tertiary = filtered_df['Tertiary_Enrollment'].mean()
internet = filtered_df['Internet_Usage'].mean()
gov      = filtered_df['Gov_Expenditure_Education'].mean()
gdp      = filtered_df['GDP_per_Capita'].mean()
upper    = filtered_df['Upper_Secondary_Completion'].mean()
urban    = filtered_df['Urban_Population'].mean()

kpi_data = [
    ("#1E40AF", "Enrollment",       f"{tertiary:.1f}%"),
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

map_col, scatter_col = st.columns(2)

# Choropleth Map 
with map_col:
    st.subheader("🌍 Global Enrollment Map")

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
        height=460,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(map_fig, use_container_width=True)

    if not map_df.empty:
        top    = map_df.loc[map_df['Tertiary_Enrollment'].idxmax()]
        bottom = map_df.loc[map_df['Tertiary_Enrollment'].idxmin()]
        st.markdown(f"""
        <div class="insight-box blue">
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

# Scatter Plot
with scatter_col:
    st.subheader(f"📈 Enrollment vs {selected_driver_label}")

    scatter_df = filtered_df.dropna(subset=['Tertiary_Enrollment', selected_driver])
    trendline_mode = "ols" if len(scatter_df) > 1 else None

    scatter_fig = px.scatter(
        scatter_df,
        x=selected_driver,
        y='Tertiary_Enrollment',
        hover_name='Country Name',
        trendline=trendline_mode,
        labels={selected_driver: selected_driver_label, 'Tertiary_Enrollment': 'Enrollment (%)'},
        color_discrete_sequence=['#3B82F6']
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
        height=460,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    corr = scatter_df[[selected_driver, 'Tertiary_Enrollment']].corr().iloc[0, 1]
    direction = "positive" if corr > 0 else "negative"
    strength  = "strong" if abs(corr) >= 0.7 else "moderate" if abs(corr) >= 0.4 else "weak"

    st.markdown(f"""
    <div class="insight-box teal">
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

# HISTORICAL TREND 

st.subheader("📉 Historical Enrollment Trend")

if selected_country == 'All':
    trend_df    = df.groupby('Year')['Tertiary_Enrollment'].mean().reset_index()
    trend_title = "Global Mean Tertiary Enrollment Over Time"
else:
    trend_df    = df[df['Country Name'] == selected_country]
    trend_title = f"Enrollment Trend — {selected_country}"

trend_fig = px.line(
    trend_df, x='Year', y='Tertiary_Enrollment',
    markers=True, title=trend_title,
    color_discrete_sequence=['#8B5CF6']
)
trend_fig.update_traces(line=dict(width=3), marker=dict(size=8))
trend_fig.update_layout(
    height=420,
    yaxis_range=[0, 110],
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
    <div class="insight-box violet">
        <h4>📉 Historical Trend Insights</h4>
        <p>
        Tertiary enrollment has <strong>{direction}</strong> from
        <strong>{start_val:.1f}%</strong> to <strong>{end_val:.1f}%</strong>
        over the observed period — an overall {tone} of
        <strong>{abs(change):.1f} percentage points</strong> in tertiary education participation.
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# CORRELATION ANALYSIS 

st.subheader("🔗 Correlation Analysis")
st.write("Visualizing the linear relationships between tertiary enrollment and socio-economic drivers.")

corr_features = [
    'Tertiary_Enrollment', 'Gov_Expenditure_Education', 'Internet_Usage', 
    'GDP_per_Capita_Log', 'Upper_Secondary_Completion', 'Urban_Population'
]

corr_df = filtered_df[corr_features].dropna()

if len(corr_df) > 1:
    corr_matrix = corr_df.corr()
    
    rename_dict = {
        'Tertiary_Enrollment': 'Enrollment',
        'Gov_Expenditure_Education': 'Edu Spending',
        'Internet_Usage': 'Internet Access',
        'GDP_per_Capita_Log': 'Log GDP per Capita',
        'Upper_Secondary_Completion': 'Upper Sec Completion',
        'Urban_Population': 'Urban Population'
    }
    corr_matrix = corr_matrix.rename(columns=rename_dict, index=rename_dict)
    
    corr_fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Blues",
        title=f"Correlation Matrix ({selected_year})"
    )
    
    corr_fig.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(corr_fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box blue">
        <h4>🔗 Correlation Insights</h4>
        <p>
        The heatmap above displays the Pearson correlation coefficients between the variables for <strong>{selected_year}</strong>. 
        Values closer to <strong>1</strong> or <strong>-1</strong> indicate stronger linear relationships with Tertiary Enrollment, 
        which helps identify key drivers before proceeding to the regression model.
        </p>
    </div>""", unsafe_allow_html=True)
else:
    st.warning("Insufficient data for correlation analysis in the selected year.")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# MULTIPLE REGRESSION 

st.subheader("🔬 Multiple Regression Analysis")
st.write("This model estimates how socio-economic indicators jointly affect tertiary enrollment across countries.")

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
            .map(
                lambda v: 'color:#10B981;font-weight:700' if v == 'Positive'
                          else 'color:#EF4444;font-weight:700',
                subset=['Relationship']
            )
            .map(
                lambda v: 'color:#10B981;font-weight:700' if isinstance(v, float) and v < 0.05
                          else 'color:gray',
                subset=['P-Value']
            ),
        use_container_width=True,
        hide_index=True
    )

    r_squared = model.rsquared
    st.markdown(f"""
    <div class="insight-box amber">
        <h4>🧠 Overall Model Performance</h4>
        <p>
        The regression model achieved an <strong>R² of {r_squared:.3f}</strong>, meaning approximately
        <strong>{r_squared*100:.1f}%</strong> of the variation in tertiary enrollment is explained
        by the five socio-economic variables included in the model.
        </p>
    </div>""", unsafe_allow_html=True)

    # Variable Interpretations 
    st.subheader("📘 Variable Interpretation")
    
    interp_cols = st.columns(2)

    for i, row in regression_table.iterrows():
        variable = row['Explanatory Variable']
        coef     = row['Coefficient']
        pval     = row['P-Value']
        relation = row['Relationship']

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
        
        with interp_cols[i % 2]:
            st.markdown(f"""
            <div class="interp-card">
                <h4>{variable}</h4>
                <p>
                A one-unit increase in <strong>{variable}</strong> is associated with an estimated
                <strong>{abs(coef):.3f}-point {pos_neg}</strong> in tertiary enrollment for
                <strong>{selected_year}</strong>.<br><br> This variable shows a
                <strong>{strength} {relation.lower()} relationship</strong> and is
                <strong>{significance}</strong> at conventional levels (p = {pval:.4f}).
                </p>
            </div>""", unsafe_allow_html=True)

else:
    st.warning("Insufficient data for regression analysis in the selected year.")
