# Mutual Fund Analytics Platform

A comprehensive Mutual Fund Analytics Platform developed as part of the Bluestock Fintech Capstone Project. The project focuses on building an end-to-end analytics pipeline using real mutual fund datasets, performing exploratory data analysis, calculating key financial performance metrics, and visualizing insights through an interactive Power BI dashboard.

---

## Project Overview

This project demonstrates the complete data analytics workflow for mutual fund analysis:

- Data ingestion and preprocessing
- ETL pipeline for cleaning and transforming datasets
- SQLite database integration
- Exploratory Data Analysis (EDA)
- Performance analytics using financial metrics
- Advanced analytics and fund recommendation
- Interactive Power BI dashboard

---

## Features

- Automated data ingestion and preprocessing
- SQLite database for structured storage
- Data cleaning and validation scripts
- Exploratory Data Analysis with multiple visualizations
- CAGR, Annualized Return, Sharpe Ratio, Beta, Alpha, VaR and CVaR calculations
- Fund comparison and ranking
- Portfolio diversification analysis
- Fund recommender system
- Interactive Power BI dashboard with multiple report pages

---

## Tech Stack

### Programming

- Python 3.x

### Libraries

- pandas
- numpy
- matplotlib
- plotly
- sqlite3
- scipy
- scikit-learn

### Database

- SQLite

### Visualization

- Power BI
- Plotly
- Matplotlib

---

## Project Structure

```
mutual-fund-analysis/
│
├── charts/
├── dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
├── notebooks/
├── reports/
├── scripts/
├── sql/
├── README.md
└── requirements.txt
```

---

## Workflow

1. Data Collection
2. Data Cleaning
3. Database Loading
4. Exploratory Data Analysis
5. Performance Metrics Calculation
6. Advanced Analytics
7. Dashboard Development
8. Final Reporting

---

## Exploratory Data Analysis

The project includes visualizations for:

- NAV Trends
- AUM Growth
- Monthly SIP Inflows
- Category-wise Inflows
- Expense Ratio Distribution
- Investor Demographics
- Geographic Distribution
- Correlation Matrix
- Sector Allocation
- Folio Growth Analysis

---

## Performance Analytics

Financial metrics implemented include:

- CAGR
- Annualized Returns
- Volatility
- Sharpe Ratio
- Beta
- Alpha
- Value at Risk (VaR)
- Conditional Value at Risk (CVaR)

---

## Advanced Analytics

The project also includes:

- Risk Analysis
- Fund Recommendation Engine
- Rolling Sharpe Analysis
- Sector Concentration Analysis
- Portfolio Diversification Insights

---

## Dashboard

The Power BI dashboard consists of four report pages:

- Industry Overview
- Fund Performance
- Investor Analytics
- SIP & Market Trends

Each page provides interactive filtering and KPI visualizations for better decision making.

---

## SQL

The project contains SQL scripts for:

- Database Schema Creation
- Data Validation
- Analytical Queries

---

## Reports

The repository includes:

- Final Project Report
- Project Presentation

---

## Future Improvements

- Live NAV updates through API scheduling
- Streamlit Web Application
- Portfolio Optimizer using Markowitz Model
- Monte Carlo NAV Forecasting
- Automated Email Reports

---
