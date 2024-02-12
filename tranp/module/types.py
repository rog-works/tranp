from dataclasses import dataclass

@dataclass
class ModulePath:
	"""モジュールパスを管理

	Attributes:
		ref_name (str): 参照名
		actual (str): 実体(実ファイルと対応)
	"""
	ref_name: str
	actual: str


class LibraryPaths(list[str]):
	"""標準ライブラリモジュールのパスリストの代替クラス。型解決以外で使用することはない"""
	...
