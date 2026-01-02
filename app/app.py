from flask import Flask, render_template, jsonify
from datetime import datetime

from data_sources import fetch_vix_close_fred, fetch_iwv_pct_change_stooq

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html", asof=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@app.get("/api/monitor")
def api_monitor():
    vix_res = fetch_vix_close_fred()
    iwv_res = fetch_iwv_pct_change_stooq()

    return jsonify({
        "asof": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # Live now:
        "iwv_pct": iwv_res.value,
        "vix": vix_res.value,

        # Phase 1 placeholders:
        "t2104": None,
        "t2117": None,
        "hh_ll": None,
        "bull20": None,
        "bear20": None,
        "stmu": None,
        "stmd": None,
        "long_ny": None,

        # Optional debugging (you can remove later)
        "errors": {
            "iwv": iwv_res.error,
            "vix": vix_res.error
        }
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
