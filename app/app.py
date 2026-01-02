from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html", asof=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.get("/api/monitor")
def api_monitor():
    # Phase 1: start with placeholders; we'll replace with real pulls next.
    return jsonify({
        "asof": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "iwv_pct": None,
        "vix": None,
        "t2104": None,
        "t2117": None,
        "hh_ll": None,
        "bull20": None,
        "bear20": None,
        "stmu": None,
        "stmd": None,
        "long_ny": None
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
EOF