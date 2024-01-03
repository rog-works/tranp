from py2cpp.lang.implementation import injectable
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node


class Module:
	"""モジュール。読み込んだモジュールのパスとエントリーポイントを管理"""

	@injectable
	def __init__(self, module_path: ModulePath, entrypoint: Node) -> None:
		"""インスタンスを生成

		Args:
			module_path (ModulePath): モジュールパス @inject
			entrypoint (Node): エントリーポイント @inject
		"""
		self.__module_path = module_path
		self.__entrypoint = entrypoint

	@property
	def path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path.ref_name

	@property
	def entrypoint(self) -> Node:
		"""Node: エントリーポイント"""
		return self.__entrypoint
