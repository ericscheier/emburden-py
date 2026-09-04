"""
Config loader for emburden-py.

Reads the shared config.yml from the emburdensynth R repo when
available (canonical source of truth for GitHub owner, PyPI owner,
package names, contact info). Falls back to bundled defaults if the
R repo isn't on the filesystem.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# Baked-in fallback matching the canonical config.yml in emburdensynth
_FALLBACK_CONFIG: dict[str, Any] = {
    "github_owner": "ericscheier",
    "github_url": "https://github.com/ericscheier",
    "pypi_owner": "ericscheier",
    "zenodo_community": "emburden",
    "packages": {
        "emburden": "emburden",
        "emburdengeo": "emburdengeo",
        "emburdendata": "emburdendata",
        "emburdenstats": "emburdenstats",
        "emburdenutil": "emburdenutil",
        "emburdenweather": "emburdenweather",
        "emburdener": "emburdener",
        "emburdenhealth": "emburdenhealth",
        "emburdenvis": "emburdenvis",
        "emburdenpub": "emburdenpub",
        "emburdentest": "emburdentest",
        "emburdenplus": "emburdenplus",
        "emburdensynth": "emburdensynth",
    },
    "python_packages": {
        "emburden": "emburden",
        "emburden_data": "emburden-data",
    },
    "maintainer": {
        "name": "Eric Scheier",
        "email": "hello@emrgi.com",
        "organization": "Emrgi",
        "organization_url": "https://emrgi.com",
    },
    "site": {
        "base_url": "https://emburden.org",
    },
    "license": "MIT",
}


def _candidate_config_paths() -> list[Path]:
    """Places to look for the canonical config.yml, in priority order."""
    candidates: list[Path] = []
    if env := os.environ.get("EMBURDEN_CONFIG"):
        candidates.append(Path(env))
    home_default = Path.home() / "Documents" / "apps" / "emburdensynth" / "config.yml"
    candidates.append(home_default)
    # Package-adjacent (installed alongside R repo)
    here = Path(__file__).resolve().parent
    for up in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        candidates.append(up / "config.yml")
        candidates.append(up.parent / "emburdensynth" / "config.yml")
    return candidates


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """
    Load the ecosystem config.

    Order of resolution:
      1. Explicit ``path`` argument
      2. ``EMBURDEN_CONFIG`` env var
      3. ``~/Documents/apps/emburdensynth/config.yml``
      4. Bundled fallback (never fails)
    """
    if path is not None:
        return yaml.safe_load(Path(path).read_text())
    for candidate in _candidate_config_paths():
        if candidate.exists():
            try:
                return yaml.safe_load(candidate.read_text())
            except Exception:
                continue
    return _FALLBACK_CONFIG


def gh_url(pkg: str | None = None, sub: str | None = None) -> str:
    """Build a GitHub URL for a package in the ecosystem."""
    cfg = load_config()
    base = cfg.get("github_url", _FALLBACK_CONFIG["github_url"])
    if pkg is None:
        return base
    repo = cfg.get("packages", {}).get(pkg, pkg)
    url = f"{base}/{repo}"
    if sub:
        url = f"{url}/{sub}"
    return url
