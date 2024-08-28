from typing import Any, MutableMapping, cast

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import implements, injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.trait import TraitProvider, Traits
from rogw.tranp.module.modules import Modules
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.processors.expand_modules import ExpandModules
from rogw.tranp.semantics.processors.resolve_unknown import ResolveUnknown
from rogw.tranp.semantics.processors.symbol_extends import SymbolExtends
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBFinalizer
from rogw.tranp.semantics.reflection.reflection import Options, Reflection, Symbol
from rogw.tranp.semantics.reflection.serialization import DictSerialized, IReflectionSerializer
from rogw.tranp.semantics.reflection.traits import export_classes
import rogw.tranp.syntax.node.definition as defs


@injectable
def preprocessors(invoker: Invoker) -> Preprocessors:
	"""プリプロセッサープロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	ctors = [
		ExpandModules,
		SymbolExtends,
		ResolveUnknown,
	]
	return lambda: [invoker(proc) for proc in ctors]


@injectable
def trait_provider(invoker: Invoker) -> TraitProvider:
	"""トレイトプロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	"""
	return lambda: [invoker(klass) for klass in export_classes()]


def plugin_provider_empty() -> PluginProvider:
	"""プラグインプロバイダーを生成(空)

	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	return lambda: []


@injectable
def symbol_db_finalizer(modules: Modules, db: SymbolDB) -> SymbolDBFinalizer:
	"""シンボルテーブル完成プロセスを実行

	Args:
		modules (Modules): モジュールマネジャー @inject
		db (SymbolDB): シンボルテーブル @inject
	Returns:
		SymbolDBFinalizer: シンボルテーブル完成プロセス
	"""
	modules.dependencies()
	return lambda: db


class ReflectionSerializer(IReflectionSerializer):
	"""シンボルシリアライザー"""

	@injectable
	def __init__(self, modules: Modules, traits: Traits) -> None:
		"""インスタンスを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
			traits (Traits): トレイトマネージャー @inject
		"""
		self._modules = modules
		self._traits = traits

	@implements
	def serialize(self, symbol: IReflection) -> DictSerialized:
		"""シリアライズ

		Args:
			symbol (IReflection): シンボル
		Returns:
			DictSerialized: データ
		"""
		if symbol.node.is_a(defs.ClassDef) and symbol.types == symbol.decl:
			return {
				'class': 'Symbol',
				'types': ModuleDSN.full_joined(symbol.types.module_path, symbol.types.full_path),
			}
		else:
			return {
				'class': 'Reflection',
				'node': ModuleDSN.full_joined(symbol.node.module_path, symbol.node.full_path),
				'decl': ModuleDSN.full_joined(symbol.decl.module_path, symbol.decl.full_path),
				'origin': symbol.types.fullyname,
				'via': symbol.via.types.fullyname,
				'attrs': [attr.types.fullyname for attr in symbol.attrs],
			}

	@implements
	def deserialize(self, db: MutableMapping[str, IReflection], data: DictSerialized) -> IReflection:
		"""デシリアライズ

		Args:
			db (MutableMapping[str, IReflection]): シンボルテーブル
			data (DictSerialized): データ
		Returns:
			IReflection: シンボル
		"""
		if data['class'] == 'Symbol':
			types_paths = ModuleDSN.parsed(data['types'])
			types = self._modules.load(types_paths[0]).entrypoint.as_a(defs.Entrypoint).whole_by(types_paths[1]).as_a(defs.ClassDef)
			symbol = Symbol.instantiate(self._traits, types)
			return symbol.stack()
		else:
			node_paths = ModuleDSN.parsed(data['node'])
			decl_paths = ModuleDSN.parsed(data['decl'])
			node = self._modules.load(node_paths[0]).entrypoint.as_a(defs.Entrypoint).whole_by(node_paths[1])
			decl = self._modules.load(decl_paths[0]).entrypoint.as_a(defs.Entrypoint).whole_by(decl_paths[1]).one_of(*defs.DeclAllTs)
			origin = db[data['origin']]
			via = db[data['via']] if data['origin'] != data['via'] else None
			attrs = [db[attr] for attr in data['attrs']]
			symbol = Reflection(self._traits, Options(node=node, decl=decl, origin=origin, via=via))
			return symbol.extends(*attrs)
