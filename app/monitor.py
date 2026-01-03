# ------------------------------------------------------------
#  Market State Logic (Rule-Based Decision Engine)
#
#  Purpose:
#  --------
#  This file converts raw market numbers into
#  simple, human-readable "states":
#
#      green  → favorable / low risk
#      yellow → neutral / caution
#      red    → unfavorable / elevated risk
#
#  Key Design Principles:
#  ----------------------
#  • No prediction
#  • No curve-fitting
#  • No optimization
#  • Clear, fixed thresholds
#  • Safe behavior when data is missing
#
#  This is where *meaning* is added to data.
# ------------------------------------------------------------


# -----------------------
#  Imports
# -----------------------
# Optional:
#   Used to clearly signal that inputs may be missing (None)
#
# Dict:
#   Used for returning a structured map of indicator states
from typing import Optional, Dict


# -----------------------
#  VIX State Logic
# -----------------------
# Input:
#   vix → most recent VIX value (float or None)
#
# Output:
#   "green"  → volatility is low
#   "yellow" → volatility elevated but manageable
#   "red"    → volatility high / unstable
#
# Threshold Rationale:
#   < 16   → complacent / calm markets
#   16–20  → rising uncertainty
#   > 20   → stress regime
def state_vix(vix: Optional[float]) -> str:
    if vix is None:
        return "gray"      # data unavailable → no judgment

    if vix < 16:
        return "green"

    if vix <= 20:
        return "yellow"

    return "red"


# -----------------------
#  IWV Percent Change State Logic
# -----------------------
# Input:
#   pct → daily % change in IWV (float or None)
#
# Output:
#   "green"  → strong positive momentum
#   "yellow" → sideways / noise
#   "red"    → negative momentum
#
# Threshold Rationale:
#   > +0.50%     → broad market strength
#   -0.50–+0.50 → normal daily noise
#   < -0.50%    → meaningful downside pressure
def state_iwv_pct(pct: Optional[float]) -> str:
    if pct is None:
        return "gray"      # missing data → display neutral

    if pct > 0.50:
        return "green"

    if pct >= -0.50:
        return "yellow"

    return "red"

# -----------------------
#  hh_ll state logic
# -----------------------
def state_hh_ll(hh_ll: Optional[float]) -> str:
    if hh_ll is None:
        return "gray"
    if hh_ll >= 100:
        return "green"
    if hh_ll <= -100:
        return "red"
    return "yellow"

# -----------------------
#  State Aggregation
# -----------------------
# Input:
#   • iwv_pct → IWV percent change
#   • vix     → VIX value
#
# Output:
#   Dictionary mapping indicator names to states:
#
#     {
#       "iwv": "yellow",
#       "vix": "green"
#     }
#
# Why:
#   This keeps the API clean and allows the frontend
#   to color rows generically without knowing logic details.
def compute_states(
        iwv_pct: Optional[float],
        vix: Optional[float],
        hh_ll: Optional[float] = None) -> Dict[str, str]:
    return {
        "iwv": state_iwv_pct(iwv_pct),
        "vix": state_vix(vix),
        "hhll": state_hh_ll(hh_ll),
    }
