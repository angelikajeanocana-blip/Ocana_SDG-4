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
/* (CSS unchanged — omitted here for brevity in explanation) */
</style>
""", unsafe_allow_html=True)

# ── TITLE ────────────────────────────────────────────────────────────────────

st.title("🎓 SDG 4: Drivers of Tertiary Enrollment")
st.write("Investigating socio-economic factors affecting tertiary school enrollment across countries")

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

st.subheader("📊 Global KPI Indicators")

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
# (UNCHANGED SECTION — keep your Plotly code as is)

# ── HISTORICAL TREND ─────────────────────────────────────────────────────────
# (UNCHANGED SECTION)

# ── MULTIPLE REGRESSION ───────────────────────────────────────────────────────

st.subheader("🔬 Multiple Regression Analysis")

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
        'Internet_Usage': 'Internet Access',
        'GDP_per_Capita_Log': 'GDP per Capita (Log)',
        'Upper_Secondary_Completion': 'Upper Secondary Completion',
        'Urban_Population': 'Urban Population'
    }

    regression_table = pd.DataFrame({
        'Explanatory Variable': [rename_map[v] for v in regression_features],
        'Coefficient': model.params.drop('const').values,
        'Std Error': model.bse.drop('const').values,
        'T-Statistic': model.tvalues.drop('const').values,
        'P-Value': model.pvalues.drop('const').values,
        'Relationship': [
            'Positive' if c > 0 else 'Negative'
            for c in model.params.drop('const').values
        ]
    })

    st.markdown('<p class="reg-title">📋 Regression Results</p>', unsafe_allow_html=True)

    # ✅ FIXED STYLING (NO applymap)
    def style_relationship(col):
        if col.name == "Relationship":
            return col.map(
                lambda v: 'color:#059669;font-weight:600'
                if v == 'Positive'
                else 'color:#DC2626;font-weight:600'
            )
        return col

    def style_pvalue(col):
        if col.name == "P-Value":
            return col.map(
                lambda v: 'color:#059669;font-weight:600'
                if isinstance(v, float) and v < 0.05
                else 'color:#5a6a8a'
            )
        return col

    st.dataframe(
        regression_table.style
            .format({
                'Coefficient': '{:.3f}',
                'Std Error': '{:.3f}',
                'T-Statistic': '{:.3f}',
                'P-Value': '{:.4f}'
            })
            .apply(style_relationship)
            .apply(style_pvalue),
        use_container_width=True,
        hide_index=True
    )

    r_squared = model.rsquared

    st.markdown(f"""
    <div class="insight-amber">
        <h4>🧠 Overall Model Performance</h4>
        <p>
        The regression model achieved an <strong>R² of {r_squared:.3f}</strong>,
        meaning approximately <strong>{r_squared*100:.1f}%</strong> of variation
        is explained by the model.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── VARIABLE INTERPRETATION ──
    st.subheader("📘 Variable Interpretation")

    for _, row in regression_table.iterrows():
        variable = row['Explanatory Variable']
        coef     = row['Coefficient']
        pval     = row['P-Value']

        strength = "strong" if abs(coef) >= 1 else "moderate" if abs(coef) >= 0.3 else "weak"
        significance = "statistically significant" if pval < 0.05 else "not statistically significant"
        direction = "increase" if coef > 0 else "decrease"

        st.markdown(f"""
        <div class="interp-card">
            <h4>{variable}</h4>
            <p>
            A one-unit increase in <strong>{variable}</strong> is associated with a
            <strong>{abs(coef):.3f} {direction}</strong> in tertiary enrollment.
            This is a <strong>{strength}</strong> and {significance} relationship.
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("Insufficient data for regression analysis in the selected year.")
