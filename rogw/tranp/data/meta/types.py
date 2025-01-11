from typing import Protocol, TypedDict


class ModuleMeta(TypedDict):
	"""モジュールのメタ情報

	Attributes:
		hash: ファイルのハッシュ値
		path: モジュールパス
	"""

	hash: str
	path: str


class TranspilerMeta(TypedDict):
	"""トランスパイラーのメタ情報

	Attributes:
		version: バージョン
		module: トランスパイラー実装クラスのモジュールパス
	"""

	version: str
	module: str


class ModuleMetaFactory(Protocol):
	"""モジュールのメタ情報ファクトリープロトコル"""

	def __call__(self, module_path: str) -> ModuleMeta:
		"""モジュールのメタ情報を生成

		Args:
			module_path: モジュールパス
		Returns:
			モジュールのメタ情報
		"""
		...
