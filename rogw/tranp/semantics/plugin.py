from typing import Protocol

from rogw.tranp.lang.eventemitter import IObservable


class IPlugin:
	"""プラグインインターフェイス"""

	def register(self, observer: IObservable) -> None:
		"""オブザーバーにプラグインを登録

		Args:
			observer (IObserver): オブザーバー
		"""
		...

	def unregister(self, observer: IObservable) -> None:
		"""オブザーバーからプラグインを解除

		Args:
			observer (IObserver): オブザーバー
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
