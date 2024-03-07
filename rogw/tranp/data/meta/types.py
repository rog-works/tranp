from typing import Protocol, TypedDict


class ModuleMeta(TypedDict):
	"""モジュールのメタ情報

	Attributes:
		hash (str): ファイルのハッシュ値
		path (str): モジュールパス
	"""

	hash: str
	path: str


class TranspilerMeta(TypedDict):
	"""トランスパイラーのメタ情報

	Attributes:
		version (str): バージョン
		module (str): トランスパイラー実装クラスのモジュールパス
	"""

	version: str
	module: str


class ModuleMetaFactory(Protocol):
	"""モジュールのメタ情報ファクトリープロトコル"""

	def __call__(self, module_path: str) -> ModuleMeta:
		"""モジュールのメタ情報を生成

		Args:
			module_path (str): モジュールパス
		Returns:
			ModuleMeta: モジュールのメタ情報
		"""
		...
