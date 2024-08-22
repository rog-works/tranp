from rogw.tranp.lang.annotation import duck_typed, implements, injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBProvider
from rogw.tranp.semantics.reflection.interface import IReflection, ITraitProvider, T_Trait, Trait
from rogw.tranp.semantics.reflection.traits import ObjectTrait


@injectable
def make_db(preprocessors: Preprocessors) -> SymbolDBProvider:
	"""シンボルテーブルを生成

	Args:
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		SymbolDBProvider: シンボルテーブルプロバイダー
	"""
	db = SymbolDB()
	for proc in preprocessors():
		db = proc(db)

	return SymbolDBProvider(db)


def plugin_provider_empty() -> PluginProvider:
	"""プラグインプロバイダーを生成(空)

	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	return lambda: []


class TraitProvider(ITraitProvider):
	"""トレイトプロバイダー"""

	@injectable
	def __init__(self, invoker: Invoker) -> None:
		"""インスタンスを生成

		Args:
			invoker (Invoker) ファクトリー関数 @inject
		"""
		self.__invoker = invoker

	@implements
	def traits(self) -> list[type[Trait]]:
		"""トレイトのクラスリストを取得

		Returns:
			list[type[Trait]]: トレイトのクラスリスト
		"""
		return [
			ObjectTrait,
		]

	@implements
	def factory(self, trait: type[T_Trait], symbol: IReflection) -> T_Trait:
		"""トレイトをインスタンス化

		Args:
			trait (type[T_Trait]): トレイトのクラス
			symbol (IReflection): 拡張対象のインスタンス
		Returns:
			T_Trait: 生成したインスタンス
		"""
		return self.__invoker(trait, symbol)
