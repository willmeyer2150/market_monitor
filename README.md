# 📊 Market Monitor

A lightweight, rule-based market monitoring dashboard built with **Python**, **Flask**, and **vanilla JavaScript**.

This project pulls a small set of market indicators, applies simple and transparent rules, and displays the results in a browser with **clear visual states** (green / yellow / red).
It is designed to be **informational, not predictive**.

---

## 🎯 Purpose & Philosophy

This project exists to answer one core question:

> **“What is the *current* market environment, using simple and repeatable rules?”**

### What this project is:

* A **market conditions monitor**
* A **learning project** for Flask, APIs, and frontend ↔ backend flow
* A **foundation** for a more advanced personal market dashboard

### What this project is *not*:

* ❌ A trading system
* ❌ A prediction engine
* ❌ An optimization or backtesting framework

### Design philosophy:

* **Consistency over precision**
* **Rules over opinions**
* **Graceful failure** when data is missing
* **Human-readable output** over dense analytics

---

## 🧠 High-Level Architecture

```
Browser (HTML + JS)
        ↓ fetch()
Flask API (/api/monitor)
        ↓
Data Sources (raw market data)
        ↓
State Logic (green / yellow / red)
        ↓
JSON response → UI update
```

Each layer has **one responsibility**.

---

## 📁 Project Structure

```
market_monitor/
│
├── app/
│   ├── app.py              # Flask app + API routes
│   ├── data_sources.py     # Raw market data pulls (no logic)
│   ├── monitor.py          # Rule-based state logic
│   ├── templates/
│   │   └── index.html      # Frontend UI
│   └── __init__.py
│
├── static/                 # (Reserved for future CSS/JS)
├── venv/                   # Python virtual environment
├── requirements.txt
└── README.md
```

---

## 🔁 How Data Flows Through the App

### 1️⃣ Browser loads the page

* `index.html` is served at `/`
* The page loads once, then updates via JavaScript

### 2️⃣ JavaScript polls the API

Every 60 seconds:

```js
fetch("/api/monitor")
```

### 3️⃣ Flask pulls market data

In `app.py`:

* VIX (volatility)
* SPY daily % change (broad market proxy)
* HH / LL (new highs minus new lows)

Each data source:

* Returns a **numeric value** or `None`
* Never crashes the app if something fails

### 4️⃣ State logic is applied

In `monitor.py`, raw numbers are converted to states:

* `"green"`
* `"yellow"`
* `"red"`
* `"gray"` (data unavailable)

### 5️⃣ JSON is returned

The API responds with:

* Raw values
* Computed states
* Optional debug errors

### 6️⃣ UI updates

* Values are displayed
* Table rows are color-coded
* Missing data shows `—` instead of breaking

---

## 📊 Indicators Explained

### SPY % Change

* **What it is**: Daily percent change of the S&P 500
* **Why it matters**: Broad U.S. market proxy

**State logic:**

| Condition        | State  |
| ---------------- | ------ |
| > +0.50%         | Green  |
| −0.50% to +0.50% | Yellow |
| < −0.50%         | Red    |

---

### VIX (Volatility Index)

* **What it is**: Market volatility expectation
* **Why it matters**: Risk / stress indicator

**State logic:**

| VIX Level | State  |
| --------- | ------ |
| < 16      | Green  |
| 16–20     | Yellow |
| > 20      | Red    |

---

### HH / LL (New Highs − New Lows)

* **What it is**:
  Number of stocks making new highs **minus** those making new lows
* **Why it matters**: Internal market breadth

#### What does a value like **4** mean?

* Example:

    * 102 stocks made new highs
    * 98 stocks made new lows
    * **HH / LL = 4**

This suggests **neutral to slightly positive breadth**, not strong participation.

**State logic:**

| HH / LL Value | State  |
| ------------- | ------ |
| ≥ +100        | Green  |
| ≤ −100        | Red    |
| Otherwise     | Yellow |

📌 **Important:**
HH/LL is noisy day-to-day. It is more useful as a *trend* than a single reading.

---

## 🧩 Why This Is Rule-Based (Not Predictive)

All thresholds are:

* Fixed
* Human-readable
* Easy to adjust
* Explicitly documented

There is **no optimization** and **no learning** happening here.
That’s intentional — this is meant to be a *situational awareness tool*.

---

## Smallest Useful Portfolio Slice

Keep the existing Flask route, rule logic, and single-page UI. Add the portfolio view to those same layers rather than introducing a database, brokerage connection, or background job.

### Manual inputs

Enter a small set of plain Python values in `app/config.py`:

* Cash balance
* Holdings: symbol, quantity, and per-share cost basis
* Watchlist rows: symbol, current price, previous close, 50-day moving average, and 200-day moving average
* One decision per holding: **hold**, **watch**, **add on weakness**, or **rebalance**

A held symbol should reuse its watchlist price data so current price is entered only once.

### Derived values

Use direct calculations in the Flask app:

* Position market value = quantity × current price
* Daily change = (current price ÷ previous close − 1) × 100
* Distance from each moving average = (current price ÷ moving average − 1) × 100
* Position weight = position market value ÷ total account value
* Cash percentage = cash ÷ total account value
* Concentration warning when one position exceeds 25% of total account value

If an input is missing or zero where division is required, display `—` rather than calculating a misleading value.

### Single-page output

Extend `app/templates/index.html` with four compact sections:

1. **Portfolio positions:** symbol, quantity, cost basis, current price, market value, and weight.
2. **Market monitor:** watchlist price, daily change, and distance from the 50-day and 200-day moving averages.
3. **Decision panel:** one row per holding with its manually selected decision.
4. **Allocation:** position weights, cash percentage, and any concentration warning.

The existing market-environment indicators remain unchanged. The first slice is complete when editing `app/config.py` and refreshing the page updates all four sections without any external portfolio or quote integration.

---

## 🧪 Error Handling & Safety

Every data pull returns a `PullResult`:

```python
PullResult(
  value: Optional[float],
  error: Optional[str]
)
```

This ensures:

* A broken data source does **not** crash the app
* The UI can degrade gracefully
* Debugging is possible without user disruption

---

## 🚀 Running the App Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask app
python app/app.py
```

Then open:

```
http://127.0.0.1:8080
```

---

## 🛠️ Current Status

✅ Flask server running
✅ Live API polling
✅ IWV, VIX, HH/LL implemented
✅ State-based coloring
🚧 Additional indicators planned (T2104, T2117, etc.)

---

## 🧭 What’s Next (Planned)

* Add more breadth indicators
* Improve historical context (rolling averages)
* Extract CSS into static files
* Possibly add a “market regime” summary
* Optional: persist snapshots for review

---

## ✍️ Final Note (For Future Me)

This project is intentionally simple.

If you ever feel tempted to:

* Add more indicators
* Add complexity
* Add predictions

**Pause and ask:**

> “Does this improve clarity, or just add noise?”

---
