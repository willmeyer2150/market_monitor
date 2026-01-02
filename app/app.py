# ------------------------------------------------------------
#  Market Monitor Web Application (Flask)
#
#  Purpose:
#  --------
#  This file defines the web-facing layer of the Market Monitor.
#  It:
#    • starts a local web server
#    • defines URL endpoints
#    • gathers market data from data_sources.py
#    • computes simple market "states" (green/yellow/red)
#    • returns HTML (for humans) and JSON (for logic/UI updates)
#
#  Philosophy:
#  -----------
#  • Consistency over precision
#  • Rule-based, not predictive
#  • Safe fallbacks when data is missing
# ------------------------------------------------------------


# -----------------------
#  Imports
# -----------------------
# Flask:
#   - Flask: main application object
#   - render_template: renders HTML files (index.html)
#   - jsonify: safely returns JSON to the browser
from flask import Flask, render_template, jsonify

# datetime:
#   Used to timestamp when data was last refreshed
from datetime import datetime

# monitor:
#   Contains logic that converts raw numbers into
#   simple "states" (green / yellow / red)
from monitor import compute_states

# data_sources:
#   Each function pulls ONE specific piece of market data
#   and returns a PullResult object (value + error info)
from data_sources import (
    fetch_vix_close_fred,
    fetch_iwv_pct_change_stooq
)


# -----------------------
#  Flask App Setup
# -----------------------
# This creates the Flask application.
# Flask uses this object to register routes and run the server.
app = Flask(__name__)


# -----------------------
#  Route: Home Page (HTML)
# -----------------------
# URL:
#   http://127.0.0.1:8080/
#
# What it does:
#   • Serves the main HTML page (index.html)
#   • Passes a timestamp into the template
#
# Why:
#   The HTML page is mostly static and uses JavaScript
#   to call /api/monitor for live updates.
@app.get("/")
def home():
    return render_template(
        "index.html",
        asof=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


# -----------------------
#  Route: Market Data API (JSON)
# -----------------------
# URL:
#   http://127.0.0.1:8080/api/monitor
#
# What it does:
#   • Pulls live market data
#   • Computes market "states"
#   • Returns everything as JSON
#
# Why:
#   This endpoint is called by JavaScript in the browser
#   to update values and colors without reloading the page.
@app.get("/api/monitor")
def api_monitor():

    # --------------------------------
    # Step 1: Fetch Raw Market Data
    # --------------------------------
    # Each function returns a PullResult:
    #   .value  -> the numeric value (or None)
    #   .error  -> error message if something failed
    vix_res = fetch_vix_close_fred()
    iwv_res = fetch_iwv_pct_change_stooq()


    # --------------------------------
    # Step 2: Compute Market States
    # --------------------------------
    # We pass ONLY the numeric values (.value),
    # not the whole PullResult object.
    #
    # compute_states() applies simple threshold rules
    # and returns:
    #   { "iwv": "yellow", "vix": "green" }
    states = compute_states(
        iwv_res.value,
        vix_res.value
    )


    # --------------------------------
    # Step 3: Return JSON Payload
    # --------------------------------
    # This dictionary becomes the JSON response.
    #
    # The browser:
    #   • reads numeric values
    #   • reads state colors
    #   • safely displays "—" when values are None
    return jsonify({

        # Timestamp (for visibility + debugging)
        "asof": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # -----------------------------
        # Live Indicators (Phase 1)
        # -----------------------------
        "iwv_pct": iwv_res.value,
        "vix": vix_res.value,

        # -----------------------------
        # Future Phase 1 Placeholders
        # -----------------------------
        # These are intentionally None for now.
        # We will layer them in gradually.
        "t2104": None,
        "t2117": None,
        "hh_ll": None,
        "bull20": None,
        "bear20": None,
        "stmu": None,
        "stmd": None,
        "long_ny": None,

        # -----------------------------
        # State Map (Green / Yellow / Red)
        # -----------------------------
        "states": states,

        # -----------------------------
        # Debug / Diagnostics (Optional)
        # -----------------------------
        # Useful while building.
        # Can be removed later without breaking anything.
        "errors": {
            "iwv": iwv_res.error,
            "vix": vix_res.error
        }
    })


# -----------------------
#  App Entry Point
# -----------------------
# This ensures the server only starts when we run:
#   python app/app.py
#
# and NOT when the file is imported elsewhere.
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=True
    )
