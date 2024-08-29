from typing import Protocol

from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath


class IModuleLoader:
	"""モジュールローダーインターフェイス"""

	def load(self, module_path: ModulePath) -> Module:
		"""モジュールをロード

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			Module: モジュール
		"""
		...

	def unload(self, module_path: ModulePath) -> None:
		"""モジュールをアンロード

		Args:
			module_path (ModulePath): モジュールパス
		"""
		...


class ModuleDependencyProvider(Protocol):
	"""モジュールの依存プロバイダープロトコル

	Note:
		* Moduleのインスタンス化に必要なモジュール定義を生成
		* ModuleLoader内で生成するDIで利用
		@see rogw.tranp.app.config.module_dependency_provider
	"""

	def __call__(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		...
