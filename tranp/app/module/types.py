from typing import NamedTuple


class ModulePath(NamedTuple):
	"""モジュールパスを管理

	Attributes:
		path: モジュールパス (書式: 'path.to.module')
		language: 言語タグ (例: 'py'=Python, 'js'=JavaScript, 'cpp'=C++)
	"""
	path: str
	language: str


class ModulePaths(list[ModulePath]):
	"""処理対象モジュールのパスリスト

	Note:
		間接的にインポートされ、暗黙的に利用されるだけのモジュールは含めない
	"""
	...


class LibraryPaths(list[ModulePath]):
	"""標準ライブラリモジュールのパスリストの代替クラス。型解決以外で使用することはない"""
	...
