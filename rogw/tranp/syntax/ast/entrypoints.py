from typing import Protocol

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.module.types import ModulePath
import rogw.tranp.syntax.node.definition as defs


class EntrypointLoader(Protocol):
	"""エントリーポイントローダープロトコル

	Note:
		* このプロトコルの実装はエントリーポイントマネージャーから利用される想定
		* エントリーポイントマネージャー以外から利用するのは非推奨
	"""

	def __call__(self, module_path: ModulePath) -> defs.Entrypoint:
		"""エントリーポイントをロード

		Args:
			module_path: モジュールパス
		Returns:
			Entrypoint: エントリーポイント
		"""
		...


class Entrypoints:
	"""エントリーポイントマネージャー

	Note:
		* このクラスはモジュールローダーからモジュール生成時に利用される想定
		* そのほか、モジュールに依存せずエントリーポイントが欲しい場合に利用
		@see rogw.tranp.module.loader.IModuleLoader
	"""

	@injectable
	def __init__(self, loader: EntrypointLoader) -> None:
		"""インスタンスを生成

		Args:
			loader: エントリーポイントローダー @inject
		"""
		self.__loader = loader
		self.__entrypoints: dict[str, defs.Entrypoint] = {}

	def load(self, module_path: str, language: str = 'py') -> defs.Entrypoint:
		"""エントリーポイントをロード

		Args:
			module_path: モジュールパス
			language: 言語タグ (default = 'py')
		Returns:
			Entrypoint: エントリーポイント
		"""
		if module_path not in self.__entrypoints:
			self.__entrypoints[module_path] = self.__loader(ModulePath(module_path, language))

		return self.__entrypoints[module_path]

	def unload(self, module_path: str) -> None:
		"""エントリーポイントをアンロード

		Args:
			module_path: モジュールパス
		"""
		if module_path in self.__entrypoints:
			del self.__entrypoints[module_path]
