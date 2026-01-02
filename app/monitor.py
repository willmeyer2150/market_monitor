from typing import Optional, Dict

def state_vix(vix: Optional[float]) -> str:
    if vix is None:
        return "gray"
    if vix < 16:
        return "green"
    if vix <= 20:
        return "yellow"
    return "red"


def state_iwv_pct(pct: Optional[float]) -> str:
    if pct is None:
        return "gray"
    if pct > 0.50:
        return "green"
    if pct >= -0.50:
        return "yellow"
    return "red"


def compute_states(iwv_pct: Optional[float], vix: Optional[float]) -> Dict[str, str]:
    return {
        "iwv": state_iwv_pct(iwv_pct),
        "vix": state_vix(vix),
    }