# Mutual Fund Analytics Data Dictionary

## 01_fund_master

| Column            | Type    | Description              |
| ----------------- | ------- | ------------------------ |
| amfi_code         | Integer | Unique AMFI Scheme Code  |
| fund_house        | Text    | AMC Name                 |
| scheme_name       | Text    | Mutual Fund Scheme Name  |
| category          | Text    | Scheme Category          |
| sub_category      | Text    | Scheme Subcategory       |
| plan              | Text    | Direct/Regular Plan      |
| expense_ratio_pct | Float   | Expense Ratio Percentage |

Source: AMFI India

---

## 02_nav_history

| Column    | Type    | Description       |
| --------- | ------- | ----------------- |
| amfi_code | Integer | Scheme Identifier |
| date      | Date    | NAV Date          |
| nav       | Float   | Net Asset Value   |

Source: MFAPI / AMFI

---

## 03_aum_by_fund_house

| Column         | Type  | Description                       |
| -------------- | ----- | --------------------------------- |
| date           | Date  | Reporting Date                    |
| fund_house     | Text  | AMC Name                          |
| aum_lakh_crore | Float | Assets Under Management           |
| aum_crore      | Float | Assets Under Management in Crores |

Source: AMFI

---

## 04_monthly_sip_inflows

Tracks monthly SIP inflows, SIP accounts and SIP AUM.

---

## 05_category_inflows

Tracks category-wise mutual fund inflows and outflows.

---

## 06_industry_folio_count

Tracks industry folio growth over time.

---

## 07_scheme_performance

Contains returns, risk metrics and ratings.

---

## 08_investor_transactions

Contains SIP, Lumpsum and Redemption transactions.

---

## 09_portfolio_holdings

Contains scheme holdings and sector allocations.

---

## 10_benchmark_indices

Contains benchmark index closing values.
