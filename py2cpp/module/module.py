from py2cpp.lang.annotation import injectable
from py2cpp.module.base import ModulePath
from py2cpp.node.node import Node


class Module:
	"""モジュール。読み込んだモジュールのパスとエントリーポイントを管理"""

	@injectable
	def __init__(self, path: ModulePath, entrypoint: Node) -> None:
		"""インスタンスを生成

		Args:
			path (ModulePath): モジュールパス @inject
			entrypoint (Node): エントリーポイント @inject
		"""
		self.__path = path
		self.__entrypoint = entrypoint

	@property
	def path(self) -> str:
		"""str: モジュールパス"""
		return self.__path

	@property
	def entrypoint(self) -> Node:
		"""Node: エントリーポイント"""
		return self.__entrypoint
