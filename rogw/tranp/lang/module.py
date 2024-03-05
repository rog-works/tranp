from importlib import import_module
import os
import sys
from typing import Any, Callable


def load_module(path: str, module: str) -> Any:
	"""モジュールをロード

	Args:
		path (str): モジュールパス
		module (str): モジュールパス
	Returns:
		Any: モジュール
	"""
	return getattr(import_module(path), module)


def load_module_path(module_path: str) -> Any:
	"""モジュールパスからモジュールをロード

	Args:
		module_path (str): モジュールパス
	Returns:
		Any: モジュール
	"""
	elems = module_path.split('.')
	path = '.'.join(elems[:-1])
	module = elems[-1]
	return load_module(path, module)


def resolve_own_class(method: Callable) -> type:
	"""メソッドからクラスを解決

	Args:
		method (Callable): メソッド
	Returns:
		type: クラス
	Raises:
		ModuleNotFoundError: 解決に失敗
	Note:
		メソッドデコレーター内ではクラスが定義中のため、クラスがモジュール内に存在しておらず解決は不可能
		メソッドデコレーター内でこの関数は使用しないこと
	"""
	modules = vars(sys.modules[method.__module__])
	class_name = method.__qualname__.split('.')[0]
	if class_name in modules:
		raise ModuleNotFoundError(f'{method.__module__}.{class_name}')

	return modules[class_name]


def fullyname(ctor: type) -> str:
	"""クラスの完全参照名を取得

	Args:
		ctor (type): クラス
	Returns:
		str: 完全参照名
	"""
	return '.'.join([ctor.__module__, ctor.__name__])


def filepath_to_module_path(filepath: str, basedir: str) -> str:
	"""モジュールのファイルパスからモジュールパスに変換

	Args:
		filepath (str): モジュールの絶対パス
		basedir (str): 基準ディレクトリーのパス
	Returns:
		str: モジュールパス
	"""
	rel_path = filepath.split(basedir)[1]
	basepath, _ = os.path.splitext(rel_path)
	elems =  [elem for elem in basepath.split(os.path.sep) if elem]
	return '.'.join(elems)
