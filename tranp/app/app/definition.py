from tranp.app.lang.di import ModuleDefinitions
from tranp.app.module.loader import ModuleDependencyProvider


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		モジュール定義
	Note:
		@see tranp.app.bin.di_defs.DIDefinitions.app
	"""
	return {
		'tranp.app.app.env.DataEnvPath': 'tranp.app.app.env.DataEnvPath',
		'tranp.app.app.env.SourceEnvPath': 'tranp.app.app.env.SourceEnvPath',
		'tranp.app.cache.cache.CacheProvider': 'tranp.app.cache.cache.CacheProvider',
		'tranp.app.cache.cache.CacheSetting': 'tranp.app.providers.cache.cache_setting',
		'tranp.app.data.meta.types.ModuleMetaFactory': 'tranp.app.providers.module.module_meta_factory',
		'tranp.app.file.loader.IDataLoader': 'tranp.app.providers.app.data_loader',
		'tranp.app.file.loader.ISourceLoader': 'tranp.app.providers.app.source_loader',
		'tranp.app.i18n.i18n.I18n': 'tranp.app.i18n.i18n.I18n',
		'tranp.app.i18n.i18n.TranslationMapping': 'tranp.app.i18n.i18n.translation_mapping_empty',
		'tranp.app.lang.trait.Traits': 'tranp.app.lang.trait.Traits',
		'tranp.app.lang.trait.TraitProvider': 'tranp.app.providers.semantics.trait_provider',
		'tranp.app.module.loader.IModuleLoader': 'tranp.app.providers.module.ModuleLoader',
		'tranp.app.module.loader.ModuleDependencyProvider': 'tranp.app.app.definition.module_dependency_provider',
		'tranp.app.module.modules.Modules': 'tranp.app.module.modules.Modules',
		'tranp.app.module.types.LibraryPaths': 'tranp.app.providers.module.library_paths',
		'tranp.app.module.types.ModulePaths': 'tranp.app.providers.module.module_paths',
		'tranp.app.semantics.reflection.db.SymbolDB': 'tranp.app.semantics.reflection.db.SymbolDB',
		'tranp.app.semantics.reflection.persistent.ISymbolDBPersistor': 'tranp.app.semantics.reflection.persistent.SymbolDBPersistor',
		'tranp.app.semantics.reflection.serialization.IReflectionSerializer': 'tranp.app.semantics.reflection.serializer.ReflectionSerializer',
		'tranp.app.semantics.finder.SymbolFinder': 'tranp.app.semantics.finder.SymbolFinder',
		'tranp.app.semantics.processor.PreprocessorProvider': 'tranp.app.providers.semantics.preprocessor_provider',
		'tranp.app.semantics.reflections.Reflections': 'tranp.app.semantics.reflections.Reflections',
		'tranp.app.syntax.ast.entrypoints.EntrypointLoader': 'tranp.app.providers.syntax.entrypoints.entrypoint_loader',
		'tranp.app.syntax.ast.entrypoints.Entrypoints': 'tranp.app.syntax.ast.entrypoints.Entrypoints',
		'tranp.app.syntax.ast.resolver.SymbolMapping': 'tranp.app.providers.syntax.resolver.symbol_mapping',
		'tranp.app.syntax.ast.parser.ParserSetting': 'tranp.app.providers.syntax.ast.parser_setting',
		'tranp.app.syntax.ast.parser.SourceProvider': 'tranp.app.providers.syntax.ast.source_provider',
		'tranp.app.syntax.ast.parser.SyntaxParser': 'tranp.app.implements.syntax.lark.parser.SyntaxParserOfLark',
		'tranp.app.transpiler.middleware.RenderMiddleware': 'tranp.app.transpiler.middleware.RenderMiddleware',
		'tranp.app.transpiler.types.Evaluator': 'tranp.app.implements.transpiler.evaluator.LiteralEvaluator',
	}


def module_dependency_provider() -> ModuleDependencyProvider:
	"""モジュールの依存プロバイダーを生成

	Returns:
		モジュールの依存プロバイダー
	Note:
		@see tranp.app.bin.di_defs.DIDefinitions.module
	"""
	return lambda: {
		'tranp.app.syntax.ast.entry.Entry': 'tranp.app.providers.syntax.ast.make_root_entry',
		'tranp.app.syntax.ast.query.Query': 'tranp.app.syntax.node.query.Nodes',
		'tranp.app.syntax.node.definition.general.Entrypoint': 'tranp.app.providers.syntax.entrypoints.entrypoint',
		'tranp.app.syntax.node.resolver.NodeResolver': 'tranp.app.syntax.node.resolver.NodeResolver',
	}
