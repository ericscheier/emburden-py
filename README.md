# emburden — Python meta-package for the emburden R ecosystem

**A thin Python shim around the [emburden R ecosystem](https://github.com/ericscheier), giving Python users a
pandas-native API for household energy-burden analytics.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/license/mit)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://pypi.org/project/emburden/)
[![emburden.org](https://img.shields.io/badge/site-emburden.org-228b22.svg)](https://emburden.org)

---

## What this is

The canonical implementation of the emburden framework is
[13 R packages](https://github.com/ericscheier). This Python package is a
lightweight bridge that lets Python users:

1. **Access precomputed synthesis outputs** as `pandas.DataFrame`s
   without needing R installed (via the companion
   [`emburden-data`](https://pypi.org/project/emburden-data/) package)
2. **Run the full pipeline** via a Python API that dispatches into R
   through [`rpy2`](https://rpy2.github.io/) (requires R + the emburden
   R packages installed)

Both paths return pandas DataFrames — you never touch rpy2 idioms.

## Install

Basic (data access only, no R required):

```bash
pip install emburden
pip install emburden-data
```

Full pipeline (needs R + the R packages):

```bash
pip install "emburden[r]"

# Then install the R side, e.g.:
Rscript -e 'remotes::install_github("ericscheier/emburdensynth")'
```

Everything:

```bash
pip install "emburden[all]"
```

## Quickstart

```python
import emburden

# What R packages are installed?
print(emburden.list_r_packages())

# If you have the data package:
df = emburden.data.load_canonical_burden()
print(df.head())

# If you have R + emburdensynth installed:
result = emburden.pipeline.run(iso3="USA", year=2023)
print(result.head())

# The 67× climate-justice mismatch headline:
metrics = emburden.pipeline.country_unified_metrics("USA")
```

## Design principles

- **R remains canonical**: this package is a thin shim, not a
  reimplementation. Changes to R semantics flow through automatically.
- **pandas-native returns**: every function returns a DataFrame, dict,
  or scalar. No rpy2 objects leak into user code.
- **Graceful degradation**: functions that need R raise clean
  `RuntimeError` when R is absent, rather than obscure ImportErrors.
- **Config-driven**: URLs + package names come from the shared
  `config.yml` in the R ecosystem repo, or from bundled fallbacks.

## What the R ecosystem does

- **`emburden`** — Net Energy Return math + reference cohort loaders
- **`emburdengeo`** — geographic infrastructure (FIPS, crosswalks)
- **`emburdendata`** — 20+ open-source downloaders (WB, Ember, OWID,
  EIA, WHO, FAOSTAT, UNDP, NASA GISTEMP, GADM, WorldPop)
- **`emburdensynth`** — 5-phase spatial-microsimulation pipeline
  covering 129 countries × 17,000 cells × 8.2bn people
- **`emburdenstats`, `emburdenutil`, `emburdenweather`,
  `emburdener`, `emburdenhealth`, `emburdenvis`, `emburdenpub`,
  `emburdentest`, `emburdenplus`** — specialized companions

See [emburden.org/code.html](https://emburden.org/code.html) for the
full package overview.

## The 67-fold climate-justice mismatch

The flagship finding from the R pipeline, computed from open data:

> On a per-capita cumulative basis, the average resident of the top-20
> historical CO₂ emitters has emitted **~67 times more cumulative CO₂**
> than the average resident of the 20 least-electrified countries.

See [emburden.org](https://emburden.org) for the interactive story and
the [80-page technical report (PDF)](https://emburden.org/global_analysis.pdf).

## Development

```bash
git clone https://github.com/ericscheier/emburden-py
cd emburden-py
pip install -e ".[dev]"
pytest
```

## License

MIT © [Eric Scheier](mailto:hello@emrgi.com) / Emrgi
