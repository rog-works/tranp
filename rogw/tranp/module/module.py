from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.types import ModulePath
from rogw.tranp.node.node import Node


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
	def module_path(self) -> ModulePath:
		"""ModulePath: モジュールパス"""
		return self.__module_path

	@property
	def path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path.ref_name

	@property
	def entrypoint(self) -> Node:
		"""Node: エントリーポイント"""
		return self.__entrypoint
