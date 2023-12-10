from importlib import import_module
from typing import Any


def load_module(path: str, module: str) -> Any:
	return getattr(import_module(path), module)


def load_module_path(module_path: str) -> Any:
	elems = module_path.split('.')
	path = '.'.join(elems[:-1])
	module = elems[-1]
	return load_module(path, module)
