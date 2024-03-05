from typing import Protocol

from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath


class ModuleLoader(Protocol):
	"""モジュールローダープロトコル"""

	def __call__(self, module_path: ModulePath) -> Module:
		"""モジュールをロード

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			Module: モジュール
		"""
		...


class ModuleDependencyProvider(Protocol):
	"""モジュールの依存プロバイダープロトコル

	Note:
		* Moduleのインスタンス化に必要なモジュール定義を生成
		* ModuleLoader内で生成するDIで利用
		@see providers.module.module_dependency_provider
	"""

	def __call__(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		...
