from typing import Protocol

from rogw.tranp.lang.eventemitter import Observable


class IPlugin:
	"""プラグインインターフェイス"""

	def register(self, observer: Observable) -> None:
		"""オブザーバーにプラグインを登録

		Args:
			observer (Observer): オブザーバー
		"""
		...

	def unregister(self, observer: Observable) -> None:
		"""オブザーバーからプラグインを解除

		Args:
			observer (Observer): オブザーバー
		"""
		...


class PluginProvider(Protocol):
	"""プラグインプロバイダー"""

	def __call__(self) -> list[IPlugin]:
		"""プラグインリストを生成

		Returns:
			list[IPlugin]: プラグインリスト
		"""
		...
