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
# Load data
# -----------------------------------------------------------
DATA_PATH = Path("data") / "bls_data.csv"

SERIES_LABELS = {
    "nonfarm_employment": "Nonfarm Employment (Thousands)",
    "unemployment_rate": "Unemployment Rate (%)",
    "labor_force_participation": "Labor Force Participation Rate (%)",
    "avg_hourly_earnings": "Average Hourly Earnings ($)",
    "avg_weekly_hours": "Average Weekly Hours",
}

# Plotly default blue (same “normal” blue most Plotly charts use)
DEFAULT_LINE_COLOR = "#1f77b4"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date")
    df["series_name"] = df["series"].map(SERIES_LABELS).fillna(df["series"])
    return df


df = load_data()

# -----------------------------------------------------------
# Sidebar: Year range + Download data
# -----------------------------------------------------------
st.sidebar.header("Filters")

start_year = int(df["date"].dt.year.min())
end_year = int(df["date"].dt.year.max())

if start_year == end_year:
    year_range = (start_year, end_year)
    st.sidebar.write(f"Only data for {start_year} is available.")
else:
    year_range = st.sidebar.slider(
        "Year range:",
        min_value=start_year,
        max_value=end_year,
        value=(start_year, end_year),
    )

# Download (all data, well cleaned & filtered)
with st.sidebar.expander("Download data", expanded=False):

    # Convert long -> wide so each series becomes its own column
    wide = (
        df.pivot(index="date", columns="series", values="value")
          .reset_index()
          .sort_values("date")
    )

    # Renameing of column name 
    wide = wide.rename(columns={
        "date": "Date",
        "avg_hourly_earnings": "Average Hourly Earnings ($)",
        "avg_weekly_hours": "Average Weekly Hours",
        "labor_force_participation": "Labor Force Participation Rate (%)",
        "nonfarm_employment": "Nonfarm Employment (Thousands)",
        "unemployment_rate": "Unemployment Rate (%)",
    })

    # Keeping only the columns I want, in the exact order
    wide = wide[
        [
            "Date",
            "Average Hourly Earnings ($)",
            "Average Weekly Hours",
            "Labor Force Participation Rate (%)",
            "Nonfarm Employment (Thousands)",
            "Unemployment Rate (%)",
        ]
    ]

    csv_all = wide.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download clean dataset (CSV)",
        data=csv_all,
        file_name="bls_data_clean.csv",
        mime="text/csv"
    )

# Filtered df for plotting (by year range only)
plot_df = df[
    (df["date"].dt.year >= year_range[0]) &
    (df["date"].dt.year <= year_range[1])
].copy()

# -----------------------------------------------------------
# Header
# -----------------------------------------------------------
st.title("📊 U.S. Labor Statistics Dashboard")
st.write(
    "Monthly data from the U.S. Bureau of Labor Statistics (BLS): employment, unemployment, "
    "labor force participation, wages, and hours since January 2020."
)

last_date = df["date"].max()
st.write(f"**Last updated:** {last_date:%B %Y}")

# -----------------------------------------------------------
# Top metrics (latest month)
# -----------------------------------------------------------
latest = df[df["date"] == last_date]


def latest_value(series_key: str):
    row = latest[latest["series"] == series_key]
    if row.empty:
        return None
    return float(row["value"].iloc[0])


m1, m2, m3 = st.columns(3)

with m1:
    v = latest_value("nonfarm_employment")
    if v is not None:
        st.metric("Nonfarm Employment (Thousands)", f"{v:,.0f}")

with m2:
    v = latest_value("unemployment_rate")
    if v is not None:
        st.metric("Unemployment Rate (%)", f"{v:.1f}")

with m3:
    v = latest_value("labor_force_participation")
    if v is not None:
        st.metric("Labor Force Participation Rate (%)", f"{v:.1f}")

st.divider()

# -----------------------------------------------------------
# Single-series line chart
# -----------------------------------------------------------
def make_line_chart(df_in: pd.DataFrame, series_key: str, title: str, y_label: str = ""):
    d = df_in[df_in["series"] == series_key].copy()
    if d.empty:
        st.info(f"No data available for {SERIES_LABELS.get(series_key, series_key)} in this year range.")
        return

    fig = px.line(
        d,
        x="date",
        y="value",
        title=title,
        labels={"date": "Date", "value": y_label},
    )

    # Clean line style (no markers), same “normal blue”
    fig.update_traces(
        line=dict(width=3, color=DEFAULT_LINE_COLOR),
        mode="lines"
    )

    # Remove extra “box feel”, keep it clean
    fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False,
        margin=dict(l=50, r=30, t=70, b=45),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------
# Tabs / Pages
# -----------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Employment Level & Status",
    "Wages & Hours",
    "Labor Utilization"
])

# --- TAB 1: Employment Level & Status (2 separate charts)
with tab1:
    st.subheader("Employment Level & Status")
    c1, c2 = st.columns(2)

    with c1:
        make_line_chart(
            plot_df,
            "nonfarm_employment",
            "Nonfarm Employment (Thousands)",
            y_label="Employment (Thousands)"
        )

    with c2:
        make_line_chart(
            plot_df,
            "unemployment_rate",
            "Unemployment Rate (%)",
            y_label="Unemployment Rate (%)"
        )

# --- TAB 2: Wages & Hours (2 separate charts)
with tab2:
    st.subheader("Wages & Hours")
    c1, c2 = st.columns(2)

    with c1:
        make_line_chart(
            plot_df,
            "avg_hourly_earnings",
            "Average Hourly Earnings ($)",
            y_label="Dollars ($)"
        )

    with c2:
        make_line_chart(
            plot_df,
            "avg_weekly_hours",
            "Average Weekly Hours",
            y_label="Hours"
        )

# --- TAB 3: Labor Utilization (1 chart + note beside it)
with tab3:
    st.subheader("Labor Utilization")

    left, right = st.columns([2, 1])

    with left:
        make_line_chart(
            plot_df,
            "labor_force_participation",
            "Labor Force Participation Rate (%)",
            y_label="Percent (%)"
        )

    with right:
        st.markdown(
            """
            **What this means (simple explanation):**  
            The **Labor Force Participation Rate (LFPR)** is the share of the working-age population
            that is either **working** or **actively looking for work**.

            - If LFPR rises: more people are entering the labor market.  
            - If LFPR falls: more people are staying out of the labor market (for example, school,
              retirement, discouragement, caregiving, etc.).  
            """
        )




