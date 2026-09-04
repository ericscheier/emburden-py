"""
R bridge for emburden-py.

Uses rpy2 when available. All R↔Python data transfer goes through
pandas, never raw rpy2 objects, so downstream users don't need to
learn rpy2 idioms.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def has_r() -> bool:
    """Return True if rpy2 is installed AND an R interpreter is reachable."""
    try:
        import rpy2.robjects  # noqa: F401
    except ImportError:
        return False
    try:
        import rpy2.robjects as ro
        ro.r("R.version.string")  # cheap sanity check
        return True
    except Exception:
        return False


def list_r_packages() -> pd.DataFrame:
    """
    Return a DataFrame of the emburden R packages installed on the
    local R side. Returns an empty DataFrame if R is unavailable.
    """
    from emburden.config import load_config

    cfg = load_config()
    pkg_names = list(cfg.get("packages", {}).values())

    if not has_r():
        return pd.DataFrame({
            "package": pkg_names,
            "installed": [False] * len(pkg_names),
            "version": [None] * len(pkg_names),
        })

    import rpy2.robjects as ro

    installed_versions = []
    for p in pkg_names:
        version = None
        try:
            ver = ro.r(f'tryCatch(as.character(utils::packageVersion("{p}")),'
                       f'error = function(e) NA_character_)')[0]
            version = None if ver == "NA" or ver is None else ver
        except Exception:
            version = None
        installed_versions.append(version)
    return pd.DataFrame({
        "package": pkg_names,
        "installed": [v is not None for v in installed_versions],
        "version": installed_versions,
    })


def call_r_function(pkg: str, func: str, **kwargs: Any) -> Any:
    """
    Call a function from an R package with Python keyword args.

    Args:
        pkg:    R package name (e.g. "emburdensynth")
        func:   function name (e.g. "run_global_pipeline")
        kwargs: keyword args passed through to R (basic types only:
                str, int, float, bool, list, dict — auto-converted
                by rpy2)

    Returns:
        The R return value, converted to Python via rpy2's default
        conversion. Callers should typically pass through r_to_pandas()
        for tabular results.

    Raises:
        RuntimeError: if rpy2 is unavailable or the R call errors.
    """
    if not has_r():
        raise RuntimeError(
            "R is not available. Install rpy2 (`pip install emburden[r]`) "
            "and ensure R + the emburden R packages are installed."
        )
    import rpy2.robjects as ro
    from rpy2.robjects import default_converter, pandas2ri
    from rpy2.robjects.conversion import localconverter

    with localconverter(default_converter + pandas2ri.converter):
        try:
            r_pkg = ro.packages.importr(pkg)
        except Exception as e:
            raise RuntimeError(f"Failed to import R package {pkg!r}: {e}") from e
        r_func = getattr(r_pkg, func, None)
        if r_func is None:
            raise RuntimeError(f"R function {pkg}::{func} not found")
        try:
            return r_func(**kwargs)
        except Exception as e:
            raise RuntimeError(f"R error in {pkg}::{func}: {e}") from e


def r_to_pandas(r_obj: Any) -> pd.DataFrame:
    """Best-effort conversion of an R object to a pandas DataFrame."""
    if not has_r():
        raise RuntimeError("R not available")
    import rpy2.robjects as ro
    from rpy2.robjects import default_converter, pandas2ri
    from rpy2.robjects.conversion import localconverter

    with localconverter(default_converter + pandas2ri.converter):
        try:
            return pd.DataFrame(ro.conversion.rpy2py(r_obj))
        except Exception:
            # Fallback: use base R as.data.frame + rpy2 auto-conversion
            return pd.DataFrame(ro.r("as.data.frame")(r_obj))
