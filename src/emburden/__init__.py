"""
emburden — Python meta-package for the emburden R ecosystem.

This is a thin shim around the R packages via rpy2. The canonical
implementation is in R at github.com/ericscheier. Python users can:

  1. Load precomputed synthesis outputs as pandas DataFrames
     (no R install required — see `emburden.data.*` or the
     sister `emburden-data` package).
  2. Run the full pipeline via `emburden.pipeline.run(iso3=...)`
     which dispatches into `emburdensynth::run_global_pipeline()` on
     the R side (requires R + the emburden R packages installed).

Design principles:
  - R remains canonical; this shim is a thin wrapper
  - Every function returns a pandas DataFrame (not an rpy2 R object)
  - Errors from R surface as Python RuntimeError with the R message

Quick start:

    import emburden
    print(emburden.__version__)
    print(emburden.list_r_packages())         # what's installed R-side

    # If you have R + emburdensynth installed:
    df = emburden.pipeline.run(iso3="USA", year=2023)
    print(df.head())

    # If you don't have R but have emburden-data:
    df = emburden.data.load_canonical_burden()
    print(df.head())

For the full R ecosystem: https://emburden.org/code.html
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Eric Scheier"
__email__ = "hello@emrgi.com"
__license__ = "MIT"

from emburden.config import load_config, gh_url
from emburden.r_bridge import (
    has_r,
    list_r_packages,
    call_r_function,
    r_to_pandas,
)

# Namespaced sub-modules
from emburden import pipeline  # noqa: F401  (import triggers module registration)

try:
    from emburden import data  # noqa: F401  (optional, needs emburden-data)
except ImportError:  # pragma: no cover
    data = None  # type: ignore

__all__ = [
    "__version__",
    "load_config",
    "gh_url",
    "has_r",
    "list_r_packages",
    "call_r_function",
    "r_to_pandas",
    "pipeline",
    "data",
]
