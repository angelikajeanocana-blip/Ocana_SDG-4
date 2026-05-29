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
    font-size: 18px;
    font-weight: 600;
}

.kpi-value {
    font-size: 30px;
    font-weight: bold;
}

.interpret-box {
    padding: 18px;
    border-radius: 12px;
    background-color: white;
    margin-bottom: 15px;
    border-left: 6px solid #2563EB;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.section-title {
    color: #1E3A8A;
    font-weight: bold;
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

# FILTER DATA

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

# MULTIPLE REGRESSION

st.markdown("""
# 📉 Multiple Regression Analysis
""")

st.markdown("""
This model estimates how different socio-economic variables affect tertiary school enrollment across countries.
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
    coefficients = model.params.drop('const')
    p_values = model.pvalues.drop('const')

    coefficient_df = pd.DataFrame({
        'Variable': coefficients.index,
        'Coefficient': coefficients.values,
        'P_Value': p_values.values
    })

    coefficient_df['Significance'] = (
        coefficient_df['P_Value']
        .apply(

            lambda p:
            'Highly Significant'
            if p < 0.01 else
            'Significant'
            if p < 0.05 else
            'Not Significant'

        )
    )

    coefficient_df['Relationship'] = (
        coefficient_df['Coefficient']
        .apply(

            lambda c:
            'Positive'
            if c > 0 else
            'Negative'
        )
    )

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

    coefficient_df['Variable'] = (
        coefficient_df['Variable']
        .map(rename_map)
    )

    # REGRESSION BAR CHART

    coefficient_fig = px.bar(

        coefficient_df,
        x='Variable',
        y='Coefficient',
        color='Relationship',
        text='Coefficient',
        hover_data=[
            'P_Value',
            'Significance'
        ],

        title='Regression Coefficients'

    )

    coefficient_fig.update_traces(
        texttemplate='%{text:.3f}',
        textposition='outside'
    )

    coefficient_fig.update_layout(
        template='plotly_white',
        height=600,
        yaxis_title='Coefficient Value',
        xaxis_title='Explanatory Variables'
    )

    st.plotly_chart(
        coefficient_fig,
        use_container_width=True
    )

    # MODEL SUMMARY

    st.markdown("""
    ## 🧠 Regression Interpretation
    """)

    r_squared = model.rsquared

    st.markdown(f"""
    <div class="interpret-box">
    <h4 class="section-title">📌 Overall Model Performance</h4>

    <b>R² = {r_squared:.3f}</b>

    <br><br>

    This means the regression model explains approximately
    <b>{r_squared*100:.1f}%</b>
    of the variation in tertiary school enrollment.

    <br><br>

    The model demonstrates a
    <b>moderately strong explanatory relationship</b>
    between the selected socio-economic variables and tertiary enrollment.
    </div>
    """, unsafe_allow_html=True)

    # VARIABLE INTERPRETATION

    st.markdown("""
    ## 📘 Variable-by-Variable Interpretation
    """)

    for _, row in coefficient_df.iterrows():
        variable = row['Variable']
        coef = row['Coefficient']
        pval = row['P_Value']
        sig = row['Significance']
        relation = row['Relationship']

        strength = abs(coef)

        if strength >= 1:
            impact = "strong"

        elif strength >= 0.3:
            impact = "moderate"

        else:
            impact = "weak"

        significance_text = (
            "statistically reliable"
            if pval < 0.05
            else "not statistically reliable"
        )

        st.markdown(f"""
        <div class="interpret-box">
        <h4 class="section-title">{variable}</h4>
        <b>Relationship:</b> {relation}<br>
        <b>Coefficient:</b> {coef:.3f}<br>
        <b>Statistical Significance:</b> {sig}<br>
        <b>P-Value:</b> {pval:.4f}<br><br>

        Interpretation:

        A one-unit increase in <b>{variable}</b>
        is associated with an estimated
        <b>{abs(coef):.3f}</b> point
        {"increase" if coef > 0 else "decrease"}
        in tertiary enrollment.

        <br><br>

        This indicates a
        <b>{impact} {relation.lower()} relationship</b>
        with tertiary enrollment.

        <br><br>

        The relationship is
        <b>{significance_text}</b>.

        </div>
        """, unsafe_allow_html=True)

    # KEY FINDINGS

    st.markdown("""
    ## 🔍 Key Findings Summary
    """)

    findings = []

    for _, row in coefficient_df.iterrows():
        if row['P_Value'] < 0.05:
            findings.append(
                f"✅ {row['Variable']} shows a statistically significant "
                f"{row['Relationship'].lower()} relationship "
                f"with tertiary enrollment."
            )

    if findings:
        for finding in findings:
            st.success(finding)
    else:
        st.warning(
            "No variables were statistically significant at p < 0.05."
        )

    with st.expander(
        "View Full Statistical OLS Summary"
    ):
        st.text(model.summary())

else:
    st.warning(
        "Insufficient data for regression analysis."
    )
