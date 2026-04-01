from app.data_sources import _get_text

symbols = [
    # common stooq-style index symbols people use (we'll test a bunch)
    "^nh", "^nl",
    "$nh", "$nl",
    "nh", "nl",
    "newhighs", "newlows",
    "hign", "lown",
    "$hign", "$lown",
    "$hign.us", "$lown.us",
    "hign.us", "lown.us",
    "^hign", "^lown",
    "nhi", "nlo",
]

def url(sym: str) -> str:
    return f"https://stooq.com/q/d/l/?s={sym}&i=d"

for s in symbols:
    try:
        text = _get_text(url(s), timeout=10)
        ok = ("Date" in text and "Close" in text and len(text.splitlines()) > 2)
        print(f"{s:12} -> {'OK' if ok else 'NO'}  (lines={len(text.splitlines())})")
        if ok:
            print("  first:", text.splitlines()[0])
            print("  last :", text.splitlines()[-1])
    except Exception as e:
        print(f"{s:12} -> ERR {e}")
