from datetime import datetime

from flask import Flask, render_template

from data_sources import (
    fetch_spy_pct_change_stooq,
    fetch_nyse_hh_ll_tv,
    fetch_vix_close_fred,
)
from monitor import compute_states

app = Flask(__name__)


@app.get("/")
def home():
    # Step 1: Get the market numbers.
    spy_result = fetch_spy_pct_change_stooq()
    vix_result = fetch_vix_close_fred()
    hh_ll_result = fetch_nyse_hh_ll_tv()

    # Step 2: Take the values out of the results.
    spy_pct = spy_result.value
    vix = vix_result.value
    hh_ll = hh_ll_result.value

    # Step 3: Decide which color each number should have.
    states = compute_states(
        spy_pct,
        vix,
        hh_ll,
    )

    # Step 4: Give everything to the HTML page.
    return render_template(
        "index.html",
        asof=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        spy_pct=spy_pct,
        vix=vix,
        hh_ll=hh_ll,
        states=states,
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=True,
    )