from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.module.loader import ModuleDependencyProvider


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		モジュール定義
	"""
	return {
		'rogw.tranp.app.env.DataEnvPath': 'rogw.tranp.providers.app.data_env_path',
		'rogw.tranp.app.env.SourceEnvPath': 'rogw.tranp.providers.app.source_env_path',
		'rogw.tranp.cache.cache.CacheProvider': 'rogw.tranp.cache.cache.CacheProvider',
		'rogw.tranp.cache.cache.CacheSetting': 'rogw.tranp.providers.cache.cache_setting',
		'rogw.tranp.data.meta.types.ModuleMetaFactory': 'rogw.tranp.providers.module.module_meta_factory',
		'rogw.tranp.file.loader.IDataLoader': 'rogw.tranp.providers.app.data_loader',
		'rogw.tranp.file.loader.ISourceLoader': 'rogw.tranp.providers.app.source_loader',
		'rogw.tranp.i18n.i18n.I18n': 'rogw.tranp.i18n.i18n.I18n',
		'rogw.tranp.i18n.i18n.TranslationMapping': 'rogw.tranp.i18n.i18n.translation_mapping_empty',
		'rogw.tranp.lang.trait.Traits': 'rogw.tranp.lang.trait.Traits',
		'rogw.tranp.lang.trait.TraitProvider': 'rogw.tranp.providers.semantics.trait_provider',
		'rogw.tranp.module.loader.IModuleLoader': 'rogw.tranp.providers.module.ModuleLoader',
		'rogw.tranp.module.loader.ModuleDependencyProvider': 'rogw.tranp.app.config.module_dependency_provider',
		'rogw.tranp.module.modules.Modules': 'rogw.tranp.module.modules.Modules',
		'rogw.tranp.module.types.LibraryPaths': 'rogw.tranp.providers.module.library_paths',
		'rogw.tranp.module.types.ModulePaths': 'rogw.tranp.providers.module.module_paths',
		'rogw.tranp.semantics.reflection.db.SymbolDB': 'rogw.tranp.semantics.reflection.db.SymbolDB',
		'rogw.tranp.semantics.reflection.persistent.ISymbolDBPersistor': 'rogw.tranp.semantics.reflection.persistent.SymbolDBPersistor',
		'rogw.tranp.semantics.reflection.serialization.IReflectionSerializer': 'rogw.tranp.semantics.reflection.serializer.ReflectionSerializer',
		'rogw.tranp.semantics.finder.SymbolFinder': 'rogw.tranp.semantics.finder.SymbolFinder',
		'rogw.tranp.semantics.plugin.PluginProvider': 'rogw.tranp.providers.semantics.plugin_provider_empty',
		'rogw.tranp.semantics.processor.PreprocessorProvider': 'rogw.tranp.providers.semantics.preprocessor_provider',
		'rogw.tranp.semantics.reflections.Reflections': 'rogw.tranp.semantics.reflections.Reflections',
		'rogw.tranp.syntax.ast.entrypoints.EntrypointLoader': 'rogw.tranp.providers.syntax.entrypoints.entrypoint_loader',
		'rogw.tranp.syntax.ast.entrypoints.Entrypoints': 'rogw.tranp.syntax.ast.entrypoints.Entrypoints',
		'rogw.tranp.syntax.ast.resolver.SymbolMapping': 'rogw.tranp.providers.syntax.resolver.symbol_mapping',
		'rogw.tranp.syntax.ast.parser.ParserSetting': 'rogw.tranp.providers.syntax.ast.parser_setting',
		'rogw.tranp.syntax.ast.parser.SourceProvider': 'rogw.tranp.providers.syntax.ast.source_provider',
		'rogw.tranp.syntax.ast.parser.SyntaxParser': 'rogw.tranp.implements.syntax.lark.parser.SyntaxParserOfLark',
	}


def module_dependency_provider() -> ModuleDependencyProvider:
	"""モジュールの依存プロバイダーを生成

	Returns:
		モジュールの依存プロバイダー
	"""
	return lambda: {
		'rogw.tranp.syntax.ast.entry.Entry': 'rogw.tranp.providers.syntax.ast.make_root_entry',
		'rogw.tranp.syntax.ast.query.Query': 'rogw.tranp.syntax.node.query.Nodes',
		'rogw.tranp.syntax.node.definition.general.Entrypoint': 'rogw.tranp.providers.syntax.entrypoints.entrypoint',
		'rogw.tranp.syntax.node.resolver.NodeResolver': 'rogw.tranp.syntax.node.resolver.NodeResolver',
	}
