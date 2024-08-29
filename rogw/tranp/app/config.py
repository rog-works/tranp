from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.module.loader import ModuleDependencyProvider


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		ModuleDefinition: モジュール定義
	"""
	return {
		'rogw.tranp.app.env.Env': 'rogw.tranp.providers.app.make_example_env',
		'rogw.tranp.data.meta.types.ModuleMetaFactory': 'rogw.tranp.providers.module.module_meta_factory',
		'rogw.tranp.i18n.i18n.I18n': 'rogw.tranp.i18n.i18n.I18n',
		'rogw.tranp.i18n.i18n.TranslationMapping': 'rogw.tranp.i18n.i18n.translation_mapping_empty',
		'rogw.tranp.io.cache.CacheProvider': 'rogw.tranp.io.cache.CacheProvider',
		'rogw.tranp.io.cache.CacheSetting': 'rogw.tranp.providers.io.cache_setting',
		'rogw.tranp.io.loader.IFileLoader': 'rogw.tranp.app.io.FileLoader',
		'rogw.tranp.lang.trait.Traits': 'rogw.tranp.lang.trait.Traits',
		'rogw.tranp.lang.trait.TraitProvider': 'rogw.tranp.providers.semantics.trait_provider',
		'rogw.tranp.module.loader.ModuleDependencyProvider': 'rogw.tranp.app.config.module_dependency_provider',
		'rogw.tranp.module.loader.ModuleLoader': 'rogw.tranp.providers.module.module_loader',
		'rogw.tranp.module.modules.Modules': 'rogw.tranp.module.modules.Modules',
		'rogw.tranp.module.types.LibraryPaths': 'rogw.tranp.providers.module.library_paths',
		'rogw.tranp.module.types.ModulePaths': 'rogw.tranp.providers.module.module_paths',
		'rogw.tranp.semantics.reflection.db.SymbolDB': 'rogw.tranp.semantics.reflection.db.SymbolDB',
		'rogw.tranp.semantics.reflection.db.SymbolDBFinalizer': 'rogw.tranp.providers.semantics.symbol_db_finalizer',
		'rogw.tranp.semantics.reflection.persistent.ISymbolDBPersistor': 'rogw.tranp.semantics.reflection.persistent.SymbolDBPersistor',
		'rogw.tranp.semantics.reflection.serialization.IReflectionSerializer': 'rogw.tranp.providers.semantics.ReflectionSerializer',
		'rogw.tranp.semantics.finder.SymbolFinder': 'rogw.tranp.semantics.finder.SymbolFinder',
		'rogw.tranp.semantics.plugin.PluginProvider': 'rogw.tranp.providers.semantics.plugin_provider_empty',
		'rogw.tranp.semantics.processor.Preprocessors': 'rogw.tranp.providers.semantics.preprocessors',
		'rogw.tranp.semantics.reflections.Reflections': 'rogw.tranp.semantics.reflections.Reflections',
		'rogw.tranp.syntax.ast.resolver.SymbolMapping': 'rogw.tranp.providers.syntax.node.symbol_mapping',
		'rogw.tranp.syntax.ast.parser.ParserSetting': 'rogw.tranp.providers.syntax.ast.parser_setting',
		'rogw.tranp.syntax.ast.parser.SourceCodeProvider': 'rogw.tranp.providers.syntax.ast.source_code_provider',
		'rogw.tranp.syntax.ast.parser.SyntaxParser': 'rogw.tranp.implements.syntax.lark.parser.SyntaxParserOfLark',
	}


def module_dependency_provider() -> ModuleDependencyProvider:
	"""モジュールの依存プロバイダーを生成

	Returns:
		ModuleDependencyProvider: モジュールの依存プロバイダー
	"""
	return lambda: {
		'rogw.tranp.module.module.Module': 'rogw.tranp.module.module.Module',
		'rogw.tranp.syntax.ast.entry.Entry': 'rogw.tranp.providers.syntax.ast.make_root_entry',
		'rogw.tranp.syntax.ast.query.Query': 'rogw.tranp.syntax.node.query.Nodes',
		'rogw.tranp.syntax.node.node.Node': 'rogw.tranp.providers.syntax.node.entrypoint',
		'rogw.tranp.syntax.node.resolver.NodeResolver': 'rogw.tranp.syntax.node.resolver.NodeResolver',
	}
