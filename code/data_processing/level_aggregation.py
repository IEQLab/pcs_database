import re
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def _normalize_level_label(level: str) -> str:
    """
    Normalize PCS level labels to canonical forms.
    - 'low' -> 'Low', 'mid'/'medium' -> 'Mid', 'high' -> 'High'
    - 'Level 3'/'level3' -> 'Level3'
    - otherwise, return stripped original with single spaces
    """
    if not isinstance(level, str):
        return level
    s = re.sub(r"\s+", " ", level.strip())
    sl = s.lower()
    if sl == "low":
        return "Low"
    if sl.startswith("mid") or sl == "medium":
        return "Mid"
    if sl == "high":
        return "High"
    m = re.match(r"level\s*(\d+)$", sl)
    if m:
        return f"Level{int(m.group(1))}"
    return s


def _parse_level_value(level_norm: str) -> float:
    """
    Map normalized level label to a sortable numeric value.
    'Low'->1, 'Mid'->2, 'High'->3, 'LevelN'->N, else alphabetical proxy.
    """
    if not isinstance(level_norm, str):
        return float("nan")
    s = level_norm
    if s in ("Low", "Mid", "High"):
        return {"Low": 1.0, "Mid": 2.0, "High": 3.0}[s]
    m = re.match(r"Level(\d+)$", s)
    if m:
        return float(int(m.group(1)))
    # fallback stable ordering by string
    return float(ord(s[0].lower()) - ord("a") + 1)


def add_level_annotations(
    df: pd.DataFrame, id_col: str = "PCS_ID", level_col: str = "PCS_Level"
) -> pd.DataFrame:
    """
    Add normalized level annotations per PCS_ID:
    - Level_Label_Normalized
    - Level_Order (1..L per device)
    - Level_Pos (0..1 scaled position across available levels; if L==1 -> 0.5)
    Returns a copy with added columns.
    """
    if level_col not in df.columns or id_col not in df.columns:
        return df.copy()

    out = df.copy()
    out["Level_Label_Normalized"] = out[level_col].apply(_normalize_level_label)

    # Build order and position maps per device
    orders: Dict[Tuple, Dict[str, int]] = {}
    positions: Dict[Tuple, Dict[str, float]] = {}

    for pcs_id, sub in out.groupby(id_col):
        levels = (
            sub["Level_Label_Normalized"].dropna().unique().tolist()
        )
        levels = sorted(levels, key=_parse_level_value)
        if not levels:
            continue
        L = len(levels)
        order_map = {lvl: i + 1 for i, lvl in enumerate(levels)}
        pos_map = {lvl: (i / (L - 1) if L > 1 else 0.5) for i, lvl in enumerate(levels)}
        orders[pcs_id] = order_map
        positions[pcs_id] = pos_map

    def _order_row(row):
        m = orders.get(row[id_col])
        if not m:
            return np.nan
        return m.get(row["Level_Label_Normalized"], np.nan)

    def _pos_row(row):
        m = positions.get(row[id_col])
        if not m:
            return np.nan
        return m.get(row["Level_Label_Normalized"], np.nan)

    out["Level_Order"] = out.apply(_order_row, axis=1)
    out["Level_Pos"] = out.apply(_pos_row, axis=1)

    return out


def compute_device_summary(
    df: pd.DataFrame,
    value_col: str = "Delta_Teq_All",
    id_col: str = "PCS_ID",
    level_norm_col: str = "Level_Label_Normalized",
    policy: str = "level_median_summary",
) -> pd.DataFrame:
    """
    Build per-device summary using per-level medians, then device stats:
    - median_device: median of per-level medians ordered by Level_Order
      (np.median averages the two central values when even)
    - min_device/max_device: min/max of per-level medians

    Returns DataFrame with columns:
      [PCS_ID, policy, median_device, min_device, max_device, n_levels]
    """
    if value_col not in df.columns or id_col not in df.columns:
        return pd.DataFrame()

    # Ensure annotations present
    if level_norm_col not in df.columns or "Level_Order" not in df.columns:
        df = add_level_annotations(df, id_col=id_col, level_col="PCS_Level")

    summaries = []

    for pcs_id, sub in df.groupby(id_col):
        sub2 = sub.dropna(subset=[value_col, level_norm_col])
        if sub2.empty:
            continue
        # per-level medians
        level_median = sub2.groupby(level_norm_col)[value_col].median()
        if level_median.empty:
            continue
        # order by Level_Order
        order_map = (
            sub2.drop_duplicates(level_norm_col)
            .set_index(level_norm_col)["Level_Order"]
            .to_dict()
        )
        med_vals = level_median.sort_index(
            key=lambda idx: [order_map.get(x, np.inf) for x in idx]
        ).values

        median_device = float(np.median(med_vals))
        min_device = float(np.min(med_vals))
        max_device = float(np.max(med_vals))

        summaries.append(
            {
                id_col: pcs_id,
                "policy": policy,
                "median_device": median_device,
                "min_device": min_device,
                "max_device": max_device,
                "n_levels": int(len(level_median)),
            }
        )

    return pd.DataFrame(summaries)
