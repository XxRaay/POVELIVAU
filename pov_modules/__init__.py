"""Реестр модулей (библиотек) языка ПОВЕЛЕВАЮ."""
from __future__ import annotations

import importlib
from typing import Callable, Dict

REGISTRY: Dict[str, Dict[str, Callable]] = {}
NODE_HANDLERS: Dict[str, Callable] = {}

# Явные соответствия имени «великой библиотеки» и Python-модуля.
MODULE_NAME_MAP = {
    'http request': 'http_request',
    'земли': 'zemli',
}


def register_module(name: str, exports: Dict[str, Callable]):
    REGISTRY[name.lower()] = exports


def register_node_handler(node_type_name: str, handler: Callable):
    NODE_HANDLERS[node_type_name] = handler


def get_node_handler(node_type_name: str):
    return NODE_HANDLERS.get(node_type_name)


def _import_module_for_library(name: str):
    module_suffix = MODULE_NAME_MAP.get(name.lower(), name.lower().replace(' ', '_'))
    importlib.import_module(f"{__name__}.{module_suffix}")


def get_exports(name: str):
    key = name.lower()
    exports = REGISTRY.get(key)
    if exports is not None:
        return exports

    try:
        _import_module_for_library(key)
    except (ImportError, ModuleNotFoundError):
        return None

    return REGISTRY.get(key)
