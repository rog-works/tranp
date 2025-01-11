from collections.abc import Callable
from importlib import import_module
import os
import sys
from typing import Any


def load_module(path: str, module: str) -> Any:
	"""モジュールをロード

	Args:
		path: モジュールパス
		module: モジュールパス
	Returns:
		Any: モジュール
	"""
	return getattr(import_module(path), module)


def load_module_path(module_path: str) -> Any:
	"""モジュールパスからモジュールをロード

	Args:
		module_path: モジュールパス
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
		method: メソッド
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


def to_fullyname(symbol: type | Callable) -> str:
	"""シンボルの完全参照名を取得

	Args:
		symbol: シンボル(クラス/ファンクション)
	Returns:
		str: 完全参照名
	"""
	return f'{symbol.__module__}.{symbol.__name__}'


def filepath_to_module_path(filepath: str, basedir: str) -> str:
	"""モジュールのファイルパスからモジュールパスに変換

	Args:
		filepath: モジュールの絶対パス
		basedir: 基準ディレクトリーのパス
	Returns:
		str: モジュールパス
	"""
	rel_path = filepath.split(basedir)[1]
	basepath, _ = os.path.splitext(rel_path)
	elems =  [elem for elem in basepath.split(os.path.sep) if elem]
	return '.'.join(elems)


def module_path_to_filepath(module_path: str, extension: str = '') -> str:
	"""モジュールパスからファイルパスに変換

	Args:
		module_path: モジュールパス
		extension: 拡張子 (default = '')
	Returns:
		str: ファイルパス
	"""
	return f'{module_path.replace('.', os.path.sep)}{extension}'
