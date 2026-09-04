"""
Thin passthrough to the emburden-data package (pure-Python data
access without needing R).

Re-exports the top-level loaders so users can write
``import emburden; df = emburden.data.load_canonical_burden()``
regardless of whether they installed emburden with or without R.
"""

from __future__ import annotations

try:
    from emburden_data import (  # noqa: F401
        load_canonical_burden,
        load_cell_grid,
        load_climate_justice_headline,
        load_owid_energy,
        load_owid_co2,
        list_datasets,
    )
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "emburden.data requires the emburden-data package. "
        "Install with: pip install emburden[data]  (or pip install emburden-data)"
    ) from e
