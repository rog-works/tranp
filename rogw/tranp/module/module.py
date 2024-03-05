from rogw.tranp.lang.implementation import injectable, override
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.node.node import Node


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
		return self.__module_path.path

	@property
	def entrypoint(self) -> Node:
		"""Node: エントリーポイント"""
		return self.__entrypoint

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.path}>'
