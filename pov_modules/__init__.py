"""Реестр модулей (библиотек) языка ПОВЕЛЕВАЮ."""
from __future__ import annotations

import importlib
import pkgutil
from typing import Callable, Dict

REGISTRY: Dict[str, Dict[str, Callable]] = {}


def register_module(name: str, exports: Dict[str, Callable]):
    REGISTRY[name.lower()] = exports


def autoload_modules():
    package_name = __name__
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith('_'):
            continue
        importlib.import_module(f"{package_name}.{module_info.name}")


def get_exports(name: str):
    return REGISTRY.get(name.lower())


autoload_modules()
