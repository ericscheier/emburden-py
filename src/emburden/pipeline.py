"""
Pipeline dispatchers — thin Python wrappers for the 5-phase
emburdensynth spatial-microsimulation pipeline.

Each function documents its R counterpart and returns pandas.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from emburden.r_bridge import call_r_function, r_to_pandas


def run(iso3: str, year: int = 2020, **kwargs) -> pd.DataFrame | None:
    """
    Run the full 5-phase pipeline for one country.

    R equivalent: ``emburdensynth::run_global_pipeline(iso3, year)``.

    Returns the resulting synthetic-household DataFrame; also writes
    the parquet output to disk as R would.
    """
    res = call_r_function("emburdensynth", "run_global_pipeline",
                          iso3=iso3, year=year, **kwargs)
    try:
        return r_to_pandas(res)
    except Exception:
        return None


def calculate_energy_insecurity_gap(iso3: str, **kwargs) -> pd.DataFrame | None:
    """
    Attach physics_required_kwh + eig_kwh + energy_limiting_flag to
    a country's synthesized parquet.

    R equivalent: ``emburdensynth::calculate_energy_insecurity_gap(iso3)``.
    """
    res = call_r_function("emburdensynth", "calculate_energy_insecurity_gap",
                          iso3=iso3, **kwargs)
    try:
        return r_to_pandas(res)
    except Exception:
        return None


def country_unified_metrics(iso3: str) -> dict:
    """
    Return the EJ-unified income/spending/required/actual/insecurity_score
    for a country.

    R equivalent: ``emburdensynth::country_unified_metrics(iso3)``.
    """
    res = call_r_function("emburdensynth", "country_unified_metrics", iso3=iso3)
    if res is None:
        return {}
    try:
        # rpy2 returns a named R list; convert to dict
        return dict(zip(res.names, list(res)))  # type: ignore[attr-defined]
    except Exception:
        return {}


def neb_divergence(df: pd.DataFrame) -> dict:
    """
    Compute the naive-vs-Nh divergence for a per-cell DataFrame.

    R equivalent: ``emburdensynth::neb_divergence(df)``.

    Args:
        df: DataFrame with columns ``hh_count``, ``expenditure_hh``,
            ``exp_Energy``, ``energy_burden``.

    Returns:
        Dict with ``naive_pct``, ``nh_pct``, ``delta_pp``, ``rel_bias_pct``.
    """
    from rpy2.robjects import default_converter, pandas2ri
    from rpy2.robjects.conversion import localconverter

    with localconverter(default_converter + pandas2ri.converter):
        res = call_r_function("emburdensynth", "neb_divergence", surface=df)
    if res is None:
        return {}
    try:
        return dict(zip(res.names, [float(x) for x in res]))  # type: ignore[attr-defined]
    except Exception:
        return {}


def available_countries() -> list[str]:
    """List ISO3 codes that have a synthetic parquet on disk."""
    from emburden.r_bridge import has_r
    if not has_r():
        return []
    import rpy2.robjects as ro
    try:
        r_files = ro.r(
            'basename(list.files("output/global", pattern = "_synthetic\\\\.parquet$"))'
        )
        return [str(x).replace("_synthetic.parquet", "") for x in r_files]
    except Exception:
        return []
