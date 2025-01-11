from typing import Protocol

from rogw.tranp.lang.eventemitter import Observable


class IPlugin:
	"""プラグインインターフェイス"""

	def register(self, observer: Observable) -> None:
		"""オブザーバーにプラグインを登録

		Args:
			observer: オブザーバー
		"""
		...

	def unregister(self, observer: Observable) -> None:
		"""オブザーバーからプラグインを解除

		Args:
			observer: オブザーバー
		"""
		...


class PluginProvider(Protocol):
	"""プラグインプロバイダー"""

	def __call__(self) -> list[IPlugin]:
		"""プラグインリストを生成

		Returns:
			プラグインリスト
		"""
		...
