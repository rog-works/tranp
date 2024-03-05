from typing import Protocol

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
