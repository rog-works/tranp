import json
import sys
from typing import Any

from tranp.app.app.definition import module_dependency_provider
from tranp.app.app.env import DataEnvPath, SourceEnvPath
from tranp.app.cache.cache import CacheProvider, CacheSetting
from tranp.app.data.meta.types import ModuleMetaFactory
from tranp.app.file.loader import IDataLoader, ISourceLoader
from tranp.app.i18n.i18n import I18n, TranslationMapping, translation_mapping_empty
from tranp.app.implements.syntax.lark.parser import SyntaxParserOfLark
from tranp.app.implements.transpiler.evaluator import LiteralEvaluator
from tranp.app.lang.module import to_fullyname
from tranp.app.lang.trait import TraitProvider, Traits
from tranp.app.module.loader import IModuleLoader, ModuleDependencyProvider
from tranp.app.module.modules import Modules
from tranp.app.module.types import LibraryPaths, ModulePaths
from tranp.app.providers.app import data_loader, source_loader
from tranp.app.providers.cache import cache_setting
from tranp.app.providers.module import ModuleLoader, library_paths, module_meta_factory, module_paths
from tranp.app.providers.semantics import preprocessor_provider, trait_provider
from tranp.app.providers.syntax.ast import make_root_entry, parser_setting, source_provider
from tranp.app.providers.syntax.entrypoints import entrypoint, entrypoint_loader
from tranp.app.providers.syntax.resolver import symbol_mapping
from tranp.app.semantics.finder import SymbolFinder
from tranp.app.semantics.processor import PreprocessorProvider
from tranp.app.semantics.reflection.db import SymbolDB
from tranp.app.semantics.reflection.persistent import ISymbolDBPersistor, SymbolDBPersistor
from tranp.app.semantics.reflection.serialization import IReflectionSerializer
from tranp.app.semantics.reflection.serializer import ReflectionSerializer
from tranp.app.semantics.reflections import Reflections
from tranp.app.syntax.ast.entry import Entry
from tranp.app.syntax.ast.entrypoints import EntrypointLoader, Entrypoints
from tranp.app.syntax.ast.parser import ParserSetting, SourceProvider, SyntaxParser
from tranp.app.syntax.ast.query import Query
from tranp.app.syntax.ast.resolver import SymbolMapping
from tranp.app.syntax.node.definition.general import Entrypoint
from tranp.app.syntax.node.query import Nodes
from tranp.app.syntax.node.resolver import NodeResolver
from tranp.app.transpiler.middleware import RenderMiddleware
from tranp.app.transpiler.types import Evaluator
	

class DIDefinitions:
	"""DI定義生成モジュール"""

	@classmethod
	def app(cls) -> dict[type[Any], Any]:
		"""DI定義を生成(アプリケーション用)

		Returns:
			DI定義
		"""
		return {
			DataEnvPath: DataEnvPath,
			SourceEnvPath: SourceEnvPath,
			CacheProvider: CacheProvider,
			CacheSetting: cache_setting,
			ModuleMetaFactory: module_meta_factory,
			IDataLoader: data_loader,
			ISourceLoader: source_loader,
			I18n: I18n,
			TranslationMapping: translation_mapping_empty,
			Traits: Traits,
			TraitProvider: trait_provider,
			IModuleLoader: ModuleLoader,
			ModuleDependencyProvider: module_dependency_provider,
			Modules: Modules,
			LibraryPaths: library_paths,
			ModulePaths: module_paths,
			SymbolDB: SymbolDB,
			ISymbolDBPersistor: SymbolDBPersistor,
			IReflectionSerializer: ReflectionSerializer,
			SymbolFinder: SymbolFinder,
			PreprocessorProvider: preprocessor_provider,
			Reflections: Reflections,
			EntrypointLoader: entrypoint_loader,
			Entrypoints: Entrypoints,
			SymbolMapping: symbol_mapping,
			ParserSetting: parser_setting,
			SourceProvider: source_provider,
			SyntaxParser: SyntaxParserOfLark,
			RenderMiddleware: RenderMiddleware,
			Evaluator: LiteralEvaluator,
		}

	@classmethod
	def module(cls) -> dict[type[Any], Any]:
		"""DI定義を生成(モジュール用)

		Returns:
			DI定義
		"""
		return {
			Entry: make_root_entry,
			Query: Nodes,
			Entrypoint: entrypoint,
			NodeResolver: NodeResolver,
		}


def run(target: str) -> None:
	"""エントリーポイント

	Args:
		target: 対象
	"""
	factories = {
		'app': DIDefinitions.app,
		'module': DIDefinitions.module,
	}
	defs = {to_fullyname(symbol): to_fullyname(injector) for symbol, injector in factories[target]().items()}
	print(json.dumps(defs, indent=2, ensure_ascii=False))


if __name__ == '__main__':
	run(sys.argv[1] if len(sys.argv) == 2 else 'app')
