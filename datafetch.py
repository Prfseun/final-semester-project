import requests
import pandas as pd
from datetime import datetime
import os

# -----------------------------------------------------------
# BLS SERIES IDs 
# -----------------------------------------------------------
SERIES = {
    "nonfarm_employment": "CES0000000001",
    "unemployment_rate": "LNS14000000",
    "labor_force_participation": "LNS11300000",
    "avg_hourly_earnings": "CES0500000003",
    "avg_weekly_hours": "CES0500000002",
}

# -----------------------------------------------------------
# Data folder if it doesn't exist
# -----------------------------------------------------------
DATA_PATH = "data/bls_data.csv"
os.makedirs("data", exist_ok=True)


# -----------------------------------------------------------
# Function to fetch BLS data for a single series
#   Now: pulls a *range* of years instead of only the latest
# -----------------------------------------------------------
def fetch_series(series_id, start_year=2020, end_year=None):
    if end_year is None:
        end_year = datetime.now().year

    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }

    response = requests.post(url, json=payload)
    data = response.json()

    rows = []

    try:
        series_data = data["Results"]["series"][0]["data"]

        # BLS returns data newest → oldest, and includes M13 (annual avg)
        for item in series_data:
            period = item["period"]  # e.g. 'M01', 'M02', ..., 'M13'
            if not period.startswith("M"):
                continue
            if period == "M13":  # skip annual average
                continue

            year = int(item["year"])
            month = int(period[1:])  # 'M01' -> 1

            date = datetime(year, month, 1)

            try:
                value = float(item["value"])
            except ValueError:
                continue

            rows.append((date, value))

    except Exception as e:
        print(f"Error fetching {series_id}: {e}")

    return rows


# -----------------------------------------------------------
# Main function — fetch all variables and save to CSV
#   Now: collects 2020–current year for every series
# -----------------------------------------------------------
def update_dataset(start_year=2020):
    all_rows = []
    end_year = datetime.now().year

    for key, series_id in SERIES.items():
        print(f"Fetching {key} from {start_year}–{end_year}...")
        series_rows = fetch_series(series_id, start_year, end_year)

        for date, value in series_rows:
            all_rows.append({
                "date": date,
                "series": key,
                "value": value,
            })

    df = pd.DataFrame(all_rows)

    # If file exists, append and drop duplicates
    if os.path.exists(DATA_PATH):
        old = pd.read_csv(DATA_PATH, parse_dates=["date"])
        df = pd.concat([old, df]).drop_duplicates(subset=["date", "series"])

    # Sort nicely by date and series
    df = df.sort_values(["date", "series"])

    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} rows to {DATA_PATH}")
    print("Data updated successfully!")


# -----------------------------------------------------------
# Run the update
# -----------------------------------------------------------
if __name__ == "__main__":
    update_dataset()

