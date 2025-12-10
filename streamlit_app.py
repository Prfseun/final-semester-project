import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------------------------------------
# Page config
# -----------------------------------------------------------
st.set_page_config(
    page_title="U.S. Labor Statistics Dashboard",
    layout="wide"
)

# -----------------------------------------------------------
# Loading of the BLS dataset
# -----------------------------------------------------------
DATA_PATH = Path("data") / "bls_data.csv"

# Human-readable labels for each series in the CSV
SERIES_LABELS = {
    "nonfarm_employment": "Nonfarm Employment (Thousands)",
    "unemployment_rate": "Unemployment Rate (%)",
    "labor_force_participation": "Labor Force Participation Rate (%)",
    "avg_hourly_earnings": "Average Hourly Earnings ($)",
    "avg_weekly_hours": "Average Weekly Hours",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date")
    # Attaching readable names for plotting and sidebar
    df["series_name"] = df["series"].map(SERIES_LABELS).fillna(df["series"])
    return df


df = load_data()

# -----------------------------------------------------------
# Header
# -----------------------------------------------------------
st.title("📊 U.S. Labor Statistics Dashboard")

st.markdown(
    """
    <p style='font-size:16px; color:#333;'>
        Monthly data from the U.S. Bureau of Labor Statistics: employment,
        unemployment, labor force participation, wages, and hours since January 2020.
    </p>
    """,
    unsafe_allow_html=True
)

last_date = df["date"].max()
st.write(f"**Last updated:** {last_date:%B %Y}")

# -----------------------------------------------------------
# Top metrics (latest month)
# -----------------------------------------------------------
latest = df[df["date"] == last_date]


def latest_value(series_key: str):
    """Get latest value for a given internal series name, e.g. 'unemployment_rate'."""
    row = latest[latest["series"] == series_key]
    if row.empty:
        return None
    return float(row["value"].iloc[0])


col1, col2, col3 = st.columns(3)

with col1:
    nf = latest_value("nonfarm_employment")
    if nf is not None:
        st.metric(
            "Nonfarm Employment (Thousands)",
            f"{nf:,.0f}",
        )

with col2:
    ur = latest_value("unemployment_rate")
    if ur is not None:
        st.metric(
            "Unemployment Rate (%)",
            f"{ur:.1f}",
        )

with col3:
    lfp = latest_value("labor_force_participation")
    if lfp is not None:
        st.metric(
            "Labor Force Participation Rate (%)",
            f"{lfp:.1f}",
        )

# -----------------------------------------------------------
# Sidebar filters
# -----------------------------------------------------------
st.sidebar.header("Filters")

# Build mapping series_key -> pretty label from the DataFrame
series_names = (
    df[["series", "series_name"]]
    .drop_duplicates()
    .set_index("series")["series_name"]
    .to_dict()
)

all_series = list(series_names.keys())

# Default selection: just nonfarm employment
default_series = ["nonfarm_employment"]

# ---- initialise session_state BEFORE widgets ----
if "series_select" not in st.session_state:
    st.session_state.series_select = [
        s for s in default_series if s in series_names
    ]

# ---- button callbacks ----
def select_all():
    st.session_state.series_select = all_series

def clear_all():
    st.session_state.series_select = []

# ---- buttons: Select all / Clear all ----
btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    st.sidebar.button("Select all", on_click=select_all)
with btn_col2:
    st.sidebar.button("Clear all", on_click=clear_all)

# ---- multiselect uses the session_state key ----
selected_series = st.sidebar.multiselect(
    "Choose series to plot:",
    options=all_series,
    format_func=lambda x: series_names.get(x, x),
    key="series_select",
)

# ---- year slider and filtering ----
start_year = int(df["date"].dt.year.min())
end_year = int(df["date"].dt.year.max())

if start_year == end_year:
    st.sidebar.write(f"Only data for {start_year} is available.")
    year_range = (start_year, end_year)
else:
    year_range = st.sidebar.slider(
        "Year range:",
        min_value=start_year,
        max_value=end_year,
        value=(max(start_year, end_year - 5), end_year),
    )

mask = (
    (df["date"].dt.year >= year_range[0])
    & (df["date"].dt.year <= year_range[1])
)

if selected_series:
    mask &= df["series"].isin(selected_series)

plot_df = df[mask]

# -----------------------------------------------------------
# Main chart
# -----------------------------------------------------------
st.subheader("Trends over time (2020–Present)")

if plot_df.empty:
    st.info("No data available for this combination of filters.")
else:
    # Build the chart title based on selected series
    if selected_series:
        readable_names = [series_names[s] for s in selected_series]
        title_text = ", ".join(readable_names)  # only the series names
    else:
        title_text = "Trends over time"

    # Create Plotly chart
    fig = px.line(
        plot_df,
        x="date",
        y="value",
        color="series_name",
        markers=True,
        title=title_text,
        labels={
            "date": "",
            "value": "",
            "series_name": "Series",
        },
    )

    # Thicker lines + nicer markers
    fig.update_traces(line=dict(width=3), marker=dict(size=6))

    # Layout: taller chart, unified hover, nice margins
    fig.update_layout(
        height=550,
        title_font_size=22,
        legend_title_text="Series",
        hovermode="x unified",
        margin=dict(l=60, r=40, t=80, b=60),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
    )

    # Adding a light rectangular border around the whole figure (chart + legend)
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="paper",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line=dict(color="#DDDDDD", width=1),
        fillcolor="rgba(250, 250, 250, 0.0)",
        layer="below",
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# Data table
# -----------------------------------------------------------
st.subheader("Data Table")

st.dataframe(
    plot_df.sort_values(["date", "series"]),
    use_container_width=True,
    height=400,
)
