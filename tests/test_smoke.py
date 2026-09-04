"""Smoke tests for emburden-py — do not require R to be installed."""

from __future__ import annotations

import pandas as pd
import pytest


def test_package_importable():
    """Basic import + version present."""
    import emburden
    assert emburden.__version__


def test_config_load():
    """Config falls back to bundled defaults even if config.yml absent."""
    from emburden.config import load_config
    cfg = load_config()
    assert cfg["github_owner"] == "ericscheier"
    assert "emburdensynth" in cfg["packages"]


def test_gh_url_helpers():
    """URL helpers produce well-formed GitHub links."""
    from emburden.config import gh_url
    assert gh_url() == "https://github.com/ericscheier"
    assert gh_url("emburdensynth") == "https://github.com/ericscheier/emburdensynth"
    assert gh_url("emburdensynth", "blob/global/README.md").endswith("README.md")


def test_has_r_returns_bool():
    """has_r() never raises even without R installed."""
    from emburden.r_bridge import has_r
    assert isinstance(has_r(), bool)


def test_list_r_packages_returns_dataframe():
    """list_r_packages returns a DataFrame (empty-ish if R absent)."""
    from emburden.r_bridge import list_r_packages
    df = list_r_packages()
    assert isinstance(df, pd.DataFrame)
    assert "package" in df.columns
    assert "installed" in df.columns
    assert "version" in df.columns
    assert len(df) >= 10  # 13 ecosystem packages, some slack for fallback


def test_call_r_function_errors_gracefully_without_r():
    """call_r_function should raise a clean RuntimeError, not import errors."""
    from emburden import r_bridge
    if r_bridge.has_r():
        pytest.skip("R is available; can't test the no-R path")
    with pytest.raises(RuntimeError):
        r_bridge.call_r_function("emburdensynth", "run_global_pipeline", iso3="USA")


def test_pipeline_module_importable():
    """Pipeline module should import even without R."""
    from emburden import pipeline
    assert callable(pipeline.run)
    assert callable(pipeline.calculate_energy_insecurity_gap)
    assert callable(pipeline.country_unified_metrics)


def test_available_countries_empty_without_r():
    """available_countries returns [] without R (not a crash)."""
    from emburden import pipeline, r_bridge
    if not r_bridge.has_r():
        assert pipeline.available_countries() == []
