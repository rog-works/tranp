from abc import ABCMeta, abstractmethod
from typing import Protocol

from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath


class IModuleLoader(metaclass=ABCMeta):
	"""モジュールローダーインターフェイス。ロード・アンロード・プリプロセスの機能を提供"""

	@abstractmethod
	def load(self, module_path: ModulePath) -> Module:
		"""モジュールをロード

		Args:
			module_path: モジュールパス
		Returns:
			Module: モジュール
		"""
		...

	@abstractmethod
	def unload(self, module_path: ModulePath) -> None:
		"""モジュールをアンロード

		Args:
			module_path: モジュールパス
		"""
		...

	@abstractmethod
	def preprocess(self, module: Module) -> None:
		"""モジュールにプリプロセスを実施

		Args:
			module: モジュール
		"""
		...


class ModuleDependencyProvider(Protocol):
	"""モジュールの依存プロバイダープロトコル

	Note:
		* Entrypointのインスタンス化に必要なモジュール定義を生成
		* EntrypointLoader内で生成するDIで利用
		@see rogw.tranp.app.config.module_dependency_provider
	"""

	def __call__(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		...
