# features/zones_finder.py
from __future__ import annotations
from typing import List, Dict, Union, Tuple, Optional
import numpy as np
import pandas as pd


def _compute_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    Wilder's ATR using OHLC. Returns the latest ATR value.
    """
    h = df["High"].to_numpy(dtype=float)
    l = df["Low"].to_numpy(dtype=float)
    c = df["Close"].to_numpy(dtype=float)

    if len(df) < period + 2:
        return float(np.nanmax(h - l)) if len(df) else 0.0

    prev_close = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum.reduce([
        h - l,
        np.abs(h - prev_close),
        np.abs(l - prev_close)
    ])
    # Wilder EMA (alpha=1/period)
    atr = pd.Series(tr).ewm(alpha=1.0 / period, adjust=False).mean().iloc[-1]
    return float(atr)


def _zone_strength(z: Dict, now_pos: int, full_price_span: float) -> float:
    """
    Heuristic strength score:
      + pivot_count, + span_frac, + recency (last touch closer = stronger), - range_pct
    Tune weights to taste.
    """
    piv = float(z.get("pivot_count", 0))
    span = float(z.get("span_frac", 0.0))                 # [0..1]
    recency = 1.0 / (1.0 + max(1, now_pos - int(z.get("last_touch_pos", now_pos))))
    rng = float(z.get("range_pct", 0.0))
    return (1.0 * piv) + (3.0 * span) + (200.0 * recency) - (2.0 * rng)


def _is_recent_window(
    df: pd.DataFrame,
    last_touch_pos: int,
    recent_months: Optional[int],
    recent_bars_per_month: int,
) -> bool:
    if recent_months is None or len(df) == 0:
        return False
    if isinstance(df.index, pd.DatetimeIndex):
        last_touch_ts = df.index[last_touch_pos]
        end_ts = df.index[-1]
        threshold = end_ts - pd.DateOffset(months=recent_months)
        return last_touch_ts >= threshold
    max_bars = int(recent_months * recent_bars_per_month)
    return (len(df) - 1 - last_touch_pos) <= max_bars


def _zone_broken(df: pd.DataFrame, last_touch_pos: int, lo: float, hi: float) -> bool:
    if last_touch_pos >= len(df) - 1:
        return False
    post = df.iloc[last_touch_pos + 1 :]
    if post.empty:
        return False
    post_highs = post["High"].to_numpy(dtype=float)
    post_lows = post["Low"].to_numpy(dtype=float)
    has_above = np.any(post_highs > hi)
    has_below = np.any(post_lows < lo)
    return bool(has_above and has_below)


def find_zones_from_pivots(
    df: pd.DataFrame,
    pivot_columns: List[str] = ("Pivot_High", "Pivot_Low"),
    # clustering & robustness
    tolerance_pct: float = 3.5,                  # acceptance band vs cluster median
    min_points: int = 4,                         # min pivots for a cluster
    q_bounds: Tuple[float, float] = (0.3, 0.7),  # robust bounds for zone (ignore outliers)
    # merging
    overlap_ratio_min: float = 0.6,              # min overlap/union to merge
    proximity_merge_pct: Optional[float] = None, # e.g., 6.0 (gap % threshold). None disables
    max_merge_range_pct: float = 6.5,            # merged band must remain tight
    min_combined_pivots: int = 7,                # min pivots after proximity-merge
    # width guards
    max_range_pct: Optional[float] = 4.0,        # drop zones wider than this %, None disables
    loose_range_pct: float = 3.0,                # if zone wider than this, require extra pivots
    extra_points_when_loose: int = 1,
    # pruning: short-span/weak zones while preserving extremes
    min_span_frac: float = 0.06,                 # ≥6% of chart OR…
    min_pivots_for_short_span: int = 6,          # …≥6 pivots if short-span
    keep_extremes: bool = True,                  # always keep absolute bottom & top by price
    # activity & volatility
    recency_window: int = 120,                   # must have a touch within last N bars
    min_retests_after_first: int = 2,            # touches after first to be considered active
    atr_period: int = 14,
    atr_mult_cap: float = 2.0,                   # height ≤ 2 * ATR
    # recent, unbroken zones (override min points and pruning)
    recent_months: Optional[int] = 3,
    recent_min_points: int = 2,
    recent_bars_per_month: int = 21,
    # output limiting
    enable_coverage_cap: bool = True,
    max_vertical_coverage: float = 0.40,         # keep zones until ≤40% of total price span
    top_k: Optional[int] = 8,                    # keep top-K strongest; None = keep all
) -> List[Dict[str, Union[int, float, object]]]:
    """
    Build precise, meaningful support/resistance zones from pivot columns.

    Returns a list of dicts:
      {
        start_index, end_index, low_price, high_price, pivot_count, range_pct,
        first_touch_pos, last_touch_pos, span_bars, span_frac,
        recent_enough, weak_short_lived, recent_unbroken, strength  (strength added near the end)
      }
    """

    # 1) collect pivots (index may be Timestamp or int)
    pivots: List[Tuple[object, float]] = []
    for col in pivot_columns:
        if col in df.columns:
            for idx, price in df[col].items():
                if not pd.isna(price):
                    pivots.append((idx, float(price)))
    if not pivots:
        return []

    # sort pivots by price asc (we’ll cluster by price proximity)
    pivots.sort(key=lambda x: x[1])

    # 2) center-based clustering with running median (prevents drift)
    clusters: List[List[Tuple[object, float]]] = []
    current: List[Tuple[object, float]] = [pivots[0]]
    cluster_min_points = min_points
    if recent_months is not None:
        cluster_min_points = min(cluster_min_points, recent_min_points)

    def _within_tol(price: float, center: float) -> bool:
        return abs(price - center) / center * 100.0 <= tolerance_pct

    for idx, price in pivots[1:]:
        center = float(np.median([p for _, p in current]))
        if _within_tol(price, center):
            current.append((idx, price))
        else:
            if len(current) >= cluster_min_points:
                clusters.append(current)
            current = [(idx, price)]
    if len(current) >= cluster_min_points:
        clusters.append(current)

    if not clusters:
        return []

    # Precompute constants
    n_last = len(df) - 1
    q_lo, q_hi = q_bounds
    atr_val = _compute_atr(df, period=atr_period)
    price_min, price_max = float(df["Low"].min()), float(df["High"].max())
    total_price_span = max(1e-12, price_max - price_min)

    # 3) clusters -> zones (robust bounds + time span + guards)
    zones: List[Dict[str, Union[int, float, object]]] = []

    for cluster in clusters:
        indices = [i for i, _ in cluster]
        prices = np.array([p for _, p in cluster], dtype=float)

        lo = float(np.quantile(prices, q_lo))
        hi = float(np.quantile(prices, q_hi))
        height = hi - lo
        range_pct = (height / lo * 100.0) if lo > 0 else 0.0

        # Time positions (first/last touch)
        positions = [df.index.get_loc(i) if not isinstance(i, int) else int(i) for i in indices]
        first_touch_pos = int(min(positions))
        last_touch_pos = int(max(positions))
        start_index = df.index[first_touch_pos] if not isinstance(df.index[first_touch_pos], (np.integer, int)) else first_touch_pos
        end_index = n_last

        # Adaptive min points for wider zones
        pivot_count = len(cluster)
        req_points = min_points + (extra_points_when_loose if range_pct > loose_range_pct else 0)
        is_recent = _is_recent_window(df, last_touch_pos, recent_months, recent_bars_per_month)
        is_unbroken = not _zone_broken(df, last_touch_pos, lo, hi)
        recent_unbroken = bool(is_recent and is_unbroken and pivot_count >= recent_min_points)
        if pivot_count < req_points and not recent_unbroken:
            continue

        # Absolute width guards
        if (max_range_pct is not None) and (range_pct > max_range_pct):
            continue
        if atr_val and height > atr_mult_cap * atr_val:
            continue

        # Retests after first touch (touch when [Low,High] intersects [lo,hi])
        post_slice = slice(first_touch_pos + 1, len(df))
        post_lows = df["Low"].iloc[post_slice].to_numpy(dtype=float)
        post_highs = df["High"].iloc[post_slice].to_numpy(dtype=float)
        post_touches = int(np.sum((post_lows <= hi) & (post_highs >= lo)))
        weak_short_lived = post_touches < min_retests_after_first

        # Recency: must have a touch recently, else considered stale (unless kept as extreme later)
        recent_enough = (len(df) - 1 - last_touch_pos) <= recency_window

        span_bars = int(last_touch_pos - first_touch_pos + 1)
        span_frac = span_bars / max(1, len(df))

        zones.append({
            "start_index": start_index,
            "end_index": end_index,
            "low_price": lo,
            "high_price": hi,
            "pivot_count": pivot_count,
            "range_pct": range_pct,
            "first_touch_pos": first_touch_pos,
            "last_touch_pos": last_touch_pos,
            "span_bars": span_bars,
            "span_frac": span_frac,
            "recent_enough": recent_enough,
            "weak_short_lived": weak_short_lived,
            "recent_unbroken": recent_unbroken,
        })

    if not zones:
        return []

    # 4) Merge zones: by overlap, and (optionally) by proximity
    zones.sort(key=lambda z: (z["low_price"], z["high_price"]))
    merged: List[Dict[str, Union[int, float, object]]] = []

    def _overlap_ratio(a: Dict, b: Dict) -> float:
        inter = max(0.0, min(a["high_price"], b["high_price"]) - max(a["low_price"], b["low_price"]))
        union = max(a["high_price"], b["high_price"]) - min(a["low_price"], b["low_price"])
        return (inter / union) if union > 0 else 0.0

    def _gap_pct(a: Dict, b: Dict) -> float:
        # assumes a below b
        if b["low_price"] <= a["high_price"]:
            return 0.0
        gap = b["low_price"] - a["high_price"]
        base = (a["high_price"] + b["low_price"]) / 2.0
        return (gap / max(1e-12, base)) * 100.0

    for z in zones:
        if not merged:
            merged.append(z)
            continue

        last = merged[-1]
        oratio = _overlap_ratio(last, z)
        can_merge_by_overlap = (oratio >= overlap_ratio_min)

        can_merge_by_proximity = False
        merged_low = min(last["low_price"], z["low_price"])
        merged_high = max(last["high_price"], z["high_price"])
        merged_range_pct = (merged_high - merged_low) / max(1e-12, merged_low) * 100.0
        combined_pivots = int(last["pivot_count"]) + int(z["pivot_count"])

        if proximity_merge_pct is not None:
            g_pct = _gap_pct(last, z)
            can_merge_by_proximity = (
                g_pct <= proximity_merge_pct
                and merged_range_pct <= max_merge_range_pct
                and combined_pivots >= min_combined_pivots
            )

        if can_merge_by_overlap or can_merge_by_proximity:
            # merge prices
            last["low_price"] = merged_low
            last["high_price"] = merged_high
            last["range_pct"] = (last["high_price"] - last["low_price"]) / max(1e-12, last["low_price"]) * 100.0

            # merge touches/time
            last["first_touch_pos"] = min(last["first_touch_pos"], z["first_touch_pos"])
            last["last_touch_pos"] = max(last["last_touch_pos"], z["last_touch_pos"])
            last["span_bars"] = int(last["last_touch_pos"] - last["first_touch_pos"] + 1)
            last["span_frac"] = last["span_bars"] / max(1, len(df))
            earliest_pos = int(last["first_touch_pos"])
            last["start_index"] = df.index[earliest_pos] if not isinstance(df.index[earliest_pos], (np.integer, int)) else earliest_pos

            # merge meta
            last["pivot_count"] = combined_pivots
            last["recent_enough"] = bool(last["recent_enough"] or z["recent_enough"])
            last["weak_short_lived"] = bool(last["weak_short_lived"] and z["weak_short_lived"])
        else:
            merged.append(z)

    if not merged:
        return []

    # 5) Prune: stale or weak short-span (keep extremes if requested)
    if keep_extremes and len(merged) >= 2:
        bottom_idx = int(np.argmin([z["low_price"] for z in merged]))
        top_idx = int(np.argmax([z["high_price"] for z in merged]))
    else:
        bottom_idx = top_idx = -1

    pruned: List[Dict[str, Union[int, float, object]]] = []
    for i, z in enumerate(merged):
        if keep_extremes and (i == bottom_idx or i == top_idx):
            pruned.append(z)
            continue
        if (not z["recent_enough"]) or z["weak_short_lived"]:
            if z.get("recent_unbroken"):
                pruned.append(z)
                continue
            continue
        if (z["span_frac"] < min_span_frac) and (z["pivot_count"] < min_pivots_for_short_span):
            if z.get("recent_unbroken"):
                pruned.append(z)
                continue
            continue
        pruned.append(z)

    if not pruned:
        return merged if keep_extremes else []

    # 6) Rank by strength & take top-K (optional)
    now_pos = len(df) - 1
    for z in pruned:
        z["strength"] = _zone_strength(z, now_pos, total_price_span)

    pruned.sort(key=lambda x: float(x["strength"]), reverse=True)
    if top_k is not None:
        pruned = pruned[:top_k]

    # 7) Coverage limiter (optional): limit total vertical coverage of kept zones
    if enable_coverage_cap and pruned:
        def _union_coverage(segs: List[Tuple[float, float]]) -> float:
            if not segs:
                return 0.0
            segs = sorted(segs)
            merged_seg = [segs[0]]
            for a, b in segs[1:]:
                c, d = merged_seg[-1]
                if a <= d:
                    merged_seg[-1] = (c, max(d, b))
                else:
                    merged_seg.append((a, b))
            return sum(b - a for a, b in merged_seg)

        kept: List[Dict] = []
        used: List[Tuple[float, float]] = []
        for z in pruned:
            candidate = used + [(float(z["low_price"]), float(z["high_price"]))]
            cov_ratio = _union_coverage(candidate) / total_price_span
            if cov_ratio <= max_vertical_coverage:
                kept.append(z)
                used = candidate
        pruned = kept if kept else pruned[: max(1, (top_k or 1))]

    return pruned
