from typing import Protocol

from rogw.tranp.module.module import Module


class ModuleLoader(Protocol):
	"""モジュールローダープロトコル"""

	def __call__(self, module_path: str) -> Module:
		"""モジュールをロード

		Args:
			module_path (str): モジュールパス
		Returns:
			Module: モジュール
		"""
		...
