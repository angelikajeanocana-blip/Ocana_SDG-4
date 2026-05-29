import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# PAGE CONFIG

st.set_page_config(
    page_title="SDG 4 Dashboard",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background-color: #f4f6f9;
}

.kpi-card {
    padding: 20px;
    border-radius: 14px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    margin-bottom: 10px;
}

.kpi-title {
    font-size: 16px;
    font-weight: 600;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
}

.insight-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #ffffff;
    border-left: 6px solid #2563EB;
    margin-top: 12px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.interpret-box {
    padding: 18px;
    border-radius: 12px;
    background-color: white;
    margin-bottom: 15px;
    border-left: 6px solid #10B981;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.section-title {
    color: #1E3A8A;
    font-weight: bold;
}

.regression-table-title {
    font-size: 22px;
    font-weight: bold;
    color: #1E3A8A;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

st.title("🎓 SDG 4: Drivers of Tertiary School Enrollment")

st.markdown("""
### Investigating Factors Affecting Tertiary Enrollment Across Countries
""")

# LOAD DATA

@st.cache_data
def load_data():

    df = pd.read_csv(
        "cleaned_tertiary_enrollment_data.csv"
    )

    df['Year'] = pd.to_numeric(
        df['Year'],
        errors='coerce'
    )

    df = df.dropna(subset=['Year'])

    df['Year'] = df['Year'].astype(int)

    required_columns = [

        'Country Name',
        'Country Code',
        'Tertiary_Enrollment',
        'Gov_Expenditure_Education',
        'Internet_Usage',
        'GDP_per_Capita',
        'Upper_Secondary_Completion',
        'Urban_Population'

    ]

    for col in required_columns:

        if col not in df.columns:
            df[col] = np.nan

    df['GDP_per_Capita_Log'] = np.log1p(
        df['GDP_per_Capita']
    )

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

country_options = ['All'] + sorted(
    df['Country Name']
    .dropna()
    .unique()
    .tolist()
)

selected_country = st.sidebar.selectbox(
    "Select Country",
    country_options
)

driver_options = {

    'Government Expenditure (% GDP)':
        'Gov_Expenditure_Education',

    'Internet Usage (% Population)':
        'Internet_Usage',

    'Log GDP per Capita':
        'GDP_per_Capita_Log',

    'Upper Secondary Completion':
        'Upper_Secondary_Completion',

    'Urban Population (%)':
        'Urban_Population'

}

selected_driver_label = st.sidebar.selectbox(
    "Choose Explanatory Driver",
    list(driver_options.keys())
)

selected_driver = driver_options[
    selected_driver_label
]

filtered_df = df[
    df['Year'] == selected_year
]

# KPI 

st.markdown("""
## 📊 Global KPI Indicators
""")

tertiary = filtered_df[
    'Tertiary_Enrollment'
].mean()

internet = filtered_df[
    'Internet_Usage'
].mean()

gov = filtered_df[
    'Gov_Expenditure_Education'
].mean()

gdp = filtered_df[
    'GDP_per_Capita'
].mean()

upper = filtered_df[
    'Upper_Secondary_Completion'
].mean()

urban = filtered_df[
    'Urban_Population'
].mean()

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="background:#1E3A8A;">
        <div class="kpi-title">Enrollment</div>
        <div class="kpi-value">{tertiary:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="background:#2563EB;">
        <div class="kpi-title">Internet</div>
        <div class="kpi-value">{internet:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="background:#10B981;">
        <div class="kpi-title">Education Spending</div>
        <div class="kpi-value">{gov:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="background:#8B5CF6;">
        <div class="kpi-title">GDP per Capita</div>
        <div class="kpi-value">${gdp:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card" style="background:#F59E0B;">
        <div class="kpi-title">Upper Secondary</div>
        <div class="kpi-value">{upper:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi6:
    st.markdown(f"""
    <div class="kpi-card" style="background:#EF4444;">
        <div class="kpi-title">Urban Population</div>
        <div class="kpi-value">{urban:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

map_col, scatter_col = st.columns(2)

# MAP

with map_col:

    map_df = filtered_df.dropna(
        subset=[
            'Country Code',
            'Tertiary_Enrollment'
        ]
    )

    map_fig = px.choropleth(

        map_df,

        locations='Country Code',

        color='Tertiary_Enrollment',

        hover_name='Country Name',

        color_continuous_scale='Plasma',

        title=f"Global Enrollment Map ({selected_year})"

    )

    map_fig.update_layout(
        template='plotly_white',
        height=500
    )

    st.plotly_chart(
        map_fig,
        use_container_width=True
    )

    # MAP INSIGHT

    if not map_df.empty:

        top_country = map_df.loc[
            map_df['Tertiary_Enrollment'].idxmax()
        ]

        bottom_country = map_df.loc[
            map_df['Tertiary_Enrollment'].idxmin()
        ]

        st.markdown(f"""
        <div class="insight-box">

        <h4>🌍 Geographic Enrollment Insights</h4>

        The choropleth map visualizes the global distribution of tertiary enrollment rates for <b>{selected_year}</b>.

        <br><br>

        <b>{top_country['Country Name']}</b> achieved one of the highest tertiary enrollment levels at
        <b>{top_country['Tertiary_Enrollment']:.1f}%</b>,
        indicating stronger higher education accessibility and participation.

        <br><br>

        Meanwhile, <b>{bottom_country['Country Name']}</b> recorded one of the lowest enrollment levels at
        <b>{bottom_country['Tertiary_Enrollment']:.1f}%</b>,
        potentially reflecting barriers in access to tertiary education.

        </div>
        """, unsafe_allow_html=True)

# SCATTER

with scatter_col:

    scatter_df = filtered_df.dropna(
        subset=[
            'Tertiary_Enrollment',
            selected_driver
        ]
    )

    trendline_mode = (
        "ols"
        if len(scatter_df) > 1
        else None
    )

    scatter_fig = px.scatter(

        scatter_df,

        x=selected_driver,
        y='Tertiary_Enrollment',

        hover_name='Country Name',

        trendline=trendline_mode,

        title=f"Enrollment vs {selected_driver_label}",

        labels={
            selected_driver:
                selected_driver_label,

            'Tertiary_Enrollment':
                'Enrollment (%)'
        }
    )

    if selected_country != 'All':

        c_df = scatter_df[
            scatter_df['Country Name']
            == selected_country
        ]

        if not c_df.empty:

            scatter_fig.add_trace(

                go.Scatter(
                    x=c_df[selected_driver],
                    y=c_df['Tertiary_Enrollment'],

                    mode='markers',

                    marker=dict(
                        color='red',
                        size=15,
                        symbol='diamond'
                    ),

                    name=selected_country
                )
            )

    scatter_fig.update_layout(
        template='plotly_white',
        height=500
    )

    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )

    # SCATTER INSIGHT

    corr = scatter_df[
        [selected_driver, 'Tertiary_Enrollment']
    ].corr().iloc[0,1]

    direction = (
        "positive"
        if corr > 0
        else "negative"
    )

    strength = (
        "strong"
        if abs(corr) >= 0.7 else
        "moderate"
        if abs(corr) >= 0.4 else
        "weak"
    )

    st.markdown(f"""
    <div class="insight-box">

    <h4>📊 Enrollment vs {selected_driver_label} Insights</h4>

    The scatter plot suggests a
    <b>{strength} {direction} relationship</b>
    between <b>{selected_driver_label}</b>
    and tertiary enrollment during <b>{selected_year}</b>.

    <br><br>

    Countries with higher values of
    <b>{selected_driver_label}</b>
    generally tend to exhibit
    {"higher" if corr > 0 else "lower"}
    tertiary enrollment rates.

    <br><br>

    Correlation coefficient:
    <b>{corr:.3f}</b>

    </div>
    """, unsafe_allow_html=True)

# HISTORICAL TREND

st.markdown("""
## 📈 Historical Enrollment Trend
""")

if selected_country == 'All':

    trend_df = df.groupby('Year')[
        'Tertiary_Enrollment'
    ].mean().reset_index()

    trend_title = "Global Mean Enrollment Trend"

else:

    trend_df = df[
        df['Country Name']
        == selected_country
    ]

    trend_title = (
        f"Enrollment Trend: {selected_country}"
    )

trend_fig = px.line(

    trend_df,

    x='Year',

    y='Tertiary_Enrollment',

    markers=True,

    title=trend_title
)

trend_fig.update_layout(
    template='plotly_white',
    height=500,
    yaxis_range=[0, 110]
)

st.plotly_chart(
    trend_fig,
    use_container_width=True
)

# TREND INSIGHT

if len(trend_df) > 1:

    start_value = trend_df[
        'Tertiary_Enrollment'
    ].iloc[0]

    end_value = trend_df[
        'Tertiary_Enrollment'
    ].iloc[-1]

    change = end_value - start_value

    direction = (
        "increased"
        if change > 0
        else "decreased"
    )

    st.markdown(f"""
    <div class="insight-box">

    <h4>📈 Historical Trend Insights</h4>

    Tertiary enrollment has
    <b>{direction}</b>
    from
    <b>{start_value:.1f}%</b>
    to
    <b>{end_value:.1f}%</b>
    over the observed time period.

    <br><br>

    This reflects an overall
    <b>{'improvement' if change > 0 else 'decline'}</b>
    in tertiary education participation trends.

    </div>
    """, unsafe_allow_html=True)

# MULTIPLE REGRESSION

st.markdown("""
# 📉 Multiple Regression Analysis
""")

st.markdown("""
This model estimates how socio-economic indicators affect tertiary enrollment across countries.
""")

regression_features = [

    'Gov_Expenditure_Education',
    'Internet_Usage',
    'GDP_per_Capita_Log',
    'Upper_Secondary_Completion',
    'Urban_Population'

]

reg_df = filtered_df[
    ['Tertiary_Enrollment']
    + regression_features
].copy()

for col in reg_df.columns:

    reg_df[col] = pd.to_numeric(
        reg_df[col],
        errors='coerce'
    )

reg_df = reg_df.dropna()

if len(reg_df) > 10:

    X = reg_df[regression_features]
    y = reg_df['Tertiary_Enrollment']

    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    rename_map = {

        'Gov_Expenditure_Education':
            'Education Spending',

        'Internet_Usage':
            'Internet Access',

        'GDP_per_Capita_Log':
            'GDP per Capita',

        'Upper_Secondary_Completion':
            'Upper Secondary Completion',

        'Urban_Population':
            'Urban Population'
    }

    regression_table = pd.DataFrame({

        'Explanatory Variable':
            [rename_map[v] for v in regression_features],

        'Coefficient':
            model.params.drop('const').values,

        'Std Error':
            model.bse.drop('const').values,

        'T-Statistic':
            model.tvalues.drop('const').values,

        'P-Value':
            model.pvalues.drop('const').values,

        'Relationship':
            [
                'Positive'
                if c > 0 else 'Negative'
                for c in model.params.drop('const').values
            ]
    })

    st.markdown("""
    <div class="regression-table-title">
    📋 Regression Results Table
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        regression_table.style.format({

            'Coefficient': '{:.3f}',
            'Std Error': '{:.3f}',
            'T-Statistic': '{:.3f}',
            'P-Value': '{:.4f}'

        }),
        use_container_width=True
    )

    # MODEL PERFORMANCE

    r_squared = model.rsquared

    st.markdown(f"""
    <div class="insight-box">

    <h4>🧠 Overall Model Performance</h4>

    The regression model achieved an
    <b>R² value of {r_squared:.3f}</b>.

    <br><br>

    This indicates that approximately
    <b>{r_squared*100:.1f}%</b>
    of the variation in tertiary enrollment
    can be explained by the socio-economic variables included in the model.

    </div>
    """, unsafe_allow_html=True)

    # VARIABLE INTERPRETATION

    st.markdown("""
    ## 📘 Interpretation of Variables
    """)

    for _, row in regression_table.iterrows():

        variable = row['Explanatory Variable']
        coef = row['Coefficient']
        pval = row['P-Value']
        relation = row['Relationship']

        strength = (
            "strong"
            if abs(coef) >= 1 else
            "moderate"
            if abs(coef) >= 0.3 else
            "weak"
        )

        significance = (
            "statistically significant"
            if pval < 0.05
            else "not statistically significant"
        )

        st.markdown(f"""
        <div class="interpret-box">

        <h4>{variable}</h4>

        A one-unit increase in
        <b>{variable}</b>
        is associated with an estimated
        <b>{abs(coef):.3f}</b> point
        {"increase" if coef > 0 else "decrease"}
        in tertiary enrollment for <b>{selected_year}</b>.

        <br><br>

        The variable demonstrates a
        <b>{strength} {relation.lower()} relationship</b>
        with tertiary enrollment and is
        <b>{significance}</b>
        at conventional statistical levels.

        </div>
        """, unsafe_allow_html=True)

    # FULL OLS SUMMARY

    with st.expander(
        "View Full OLS Statistical Summary"
    ):
        st.text(model.summary())

else:

    st.warning(
        "Insufficient data for regression analysis."
    )
