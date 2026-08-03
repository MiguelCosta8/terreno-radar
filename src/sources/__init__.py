from __future__ import annotations

from .base import BaseSource
from .casasapo import CasaSapoSource
from .imovirtual import ImovirtualSource

# Register each source under the key you use in config.yaml -> searches[].source
REGISTRY: dict[str, BaseSource] = {
    "casasapo": CasaSapoSource(),
    "imovirtual": ImovirtualSource(),
}


def get_source(name: str) -> BaseSource:
    if name not in REGISTRY:
        raise KeyError(f"Unknown source '{name}'. Known: {sorted(REGISTRY)}")
    return REGISTRY[name]
