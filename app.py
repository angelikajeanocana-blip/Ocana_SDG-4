import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# PAGE CONFIGURATION

st.set_page_config(
    page_title="SDG 4 Dashboard",
    layout="wide"
)

st.title("SDG 4: Drivers of Tertiary School Enrollment")

st.markdown("""
Investigating Factors Affecting Tertiary Enrollment Across Countries
""")

# LOAD DATA

@st.cache_data
def load_data():

    df = pd.read_csv("cleaned_tertiary_enrollment_data.csv")

    # Clean year
    df['Year'] = pd.to_numeric(
        df['Year'],
        errors='coerce'
    )

    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)

    # Ensure required columns exist
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

    # Safe log GDP
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
    df['Country Name'].dropna().unique().tolist()
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

selected_driver = driver_options[selected_driver_label]

# FILTER DATA

filtered_df = df[
    df['Year'] == selected_year
]

# KPI SECTION

st.subheader("Global KPI Indicators")

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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tertiary Enrollment",
        f"{tertiary:.1f}%"
    )

    st.metric(
        "Internet Usage",
        f"{internet:.1f}%"
    )

with col2:
    st.metric(
        "Education Spending",
        f"{gov:.1f}%"
    )

    st.metric(
        "GDP per Capita",
        f"${gdp:,.0f}"
    )

with col3:
    st.metric(
        "Upper Secondary Completion",
        f"{upper:.1f}%"
    )

    st.metric(
        "Urban Population",
        f"{urban:.1f}%"
    )

map_col, scatter_col = st.columns(2)

# CHOROPLETH MAP

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

        title=f"Global Tertiary Enrollment ({selected_year})"

    )

    map_fig.update_layout(
        height=500
    )

    st.plotly_chart(
        map_fig,
        use_container_width=True
    )

# SCATTER PLOT

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
        title=f"Tertiary Enrollment vs {selected_driver_label}",

        labels={
            selected_driver:
                selected_driver_label,

            'Tertiary_Enrollment':
                'Enrollment (%)'
        }

    )

    # Highlight selected country

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
        height=500,
        template='plotly_white'
    )

    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )

# HISTORICAL TREND

st.subheader("Historical Enrollment Trend")

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

st.subheader(
    "Multiple Regression Analysis"
)

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

# Force numeric
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
        height=600
    )

    st.plotly_chart(
        coefficient_fig,
        use_container_width=True
    )

    # REGRESSION SUMMARY

    st.subheader("Regression Interpretation")

    st.dataframe(
        coefficient_df,
        use_container_width=True
    )
    st.text(model.summary())

else:
    st.warning(
        "Insufficient data for regression analysis."
    )
