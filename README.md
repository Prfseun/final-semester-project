# U.S. Labor Statistics Dashboard

This repository contains a Streamlit dashboard developed for **ECON 8320 – Tools for Data Analysis**.

## Project Overview
The dashboard visualizes monthly U.S. labor market indicators obtained from the **U.S. Bureau of Labor Statistics (BLS)**, including:
- Nonfarm employment
- Unemployment rate
- Labor force participation rate
- Additional labor market series - Average Hourly Earnings ($) and Average Weekly Hours

The dashboard allows users to:
- Select which labor market variables to display using interactive filters
- Adjust the year range (from 2020 to the most recent data) using a slider
- View updated trends as new BLS data becomes available

## Automated Data Updates
This project uses **GitHub Actions** to automatically:
- Collect new BLS data **once per month** when new data is released
- Append the new data to the existing dataset stored in the repository
- Ensure the dashboard reflects updated data without re-collecting data on each page load

## Repository Structure
- `datafetch.py` – Script to collect and append BLS data
- `data/bls_data.csv` – Stored dataset updated monthly
- `streamlit_app.py` – Streamlit dashboard application
- `.github/workflows/update_bls.yml` – GitHub Actions workflow for monthly updates

## Live Dashboard
The Streamlit dashboard is deployed using **Streamlit Community Cloud** and is publicly accessible. Here is the link: https://seunakinbowale-semester-project.streamlit.app/

## Author
Seun Jide Akinbowale  
ECON 8320 – Tools for Data Analysis
