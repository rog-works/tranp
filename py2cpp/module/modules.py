from typing import cast

from py2cpp.lang.annotation import injectable
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Curry, Locator
from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import SyntaxParser
from py2cpp.module.base import ModulePath
from py2cpp.module.provider import CoreLibrariesProvider
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
		"""Node: エントリーポイントを取得"""
		return self.__entrypoint


class Modules:
	"""モジュールマネージャー。メインモジュールを基点として関連するインポートモジュールを管理"""

	@injectable
	def __init__(self, locator: Locator, parser: SyntaxParser) -> None:
		"""インスタンスを生成

		Args:
			locator (Locator): ロケーター @inject
			parser (SyntaxParser): シンタックスパーサー @inject
		"""
		self.__modules: dict[str, Module] = {}
		self.__locator = locator
		self.__parser = parser

	@property
	def main(self) -> Module:
		"""Module: メインモジュール"""
		# FIXME Modules以外がモジュールを管理しているのは微妙
		return self.__locator.resolve(Module)

	@property
	def imported(self) -> list[Module]:
		"""list[Module]: インポート済みのモジュールリスト"""
		return list(self.__modules.values())

	@property
	def core_libralies(self) -> list[Module]:
		paths = self.__locator.resolve(CoreLibrariesProvider)()
		return [self.load(path) for path in paths]

	def load(self, module_path: str) -> Module:
		if module_path not in self.__modules:
			self.__modules[module_path] = self.__load_impl(module_path)

		return self.__modules[module_path]

	def __load_impl(self, module_path: str) -> Module:
		root = self.__parser.parse(module_path)
		di = cast(DI, self.__locator).clone()
		di.rebind(Locator, lambda: di)
		di.rebind(Curry, lambda: di.curry)
		di.rebind(ModulePath, lambda: module_path)
		di.rebind(Module, Module)
		di.rebind(Entry, lambda: root)
		return di.resolve(Module)
