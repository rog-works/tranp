from rogw.tranp.lang.di import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		ModuleDefinition: モジュール定義
	"""
	return {
		'rogw.tranp.app.env.Env': 'rogw.tranp.providers.app.make_env',
		'rogw.tranp.i18n.i18n.I18n': 'rogw.tranp.i18n.i18n.I18n',
		'rogw.tranp.i18n.i18n.TranslationMapping': 'rogw.tranp.i18n.i18n.translation_mapping_empty',
		'rogw.tranp.io.cache.CacheProvider': 'rogw.tranp.io.cache.CacheProvider',
		'rogw.tranp.io.cache.CacheSetting': 'rogw.tranp.providers.io.cache_setting',
		'rogw.tranp.io.loader.IFileLoader': 'rogw.tranp.app.io.FileLoader',
		'rogw.tranp.module.loader.ModuleLoader': 'rogw.tranp.providers.module.module_loader',
		'rogw.tranp.module.modules.Modules': 'rogw.tranp.module.modules.Modules',
		'rogw.tranp.module.types.LibraryPaths': 'rogw.tranp.providers.module.library_paths',
		'rogw.tranp.module.types.ModulePaths': 'rogw.tranp.providers.module.module_paths',
		'rogw.tranp.semantics.finder.SymbolFinder': 'rogw.tranp.semantics.finder.SymbolFinder',
		'rogw.tranp.semantics.plugin.PluginProvider': 'rogw.tranp.semantics.plugin.plugin_provider_empty',
		'rogw.tranp.semantics.processor.Preprocessors': 'rogw.tranp.semantics.preprocessors.preprocessors',
		'rogw.tranp.semantics.reflection.interface.SymbolDBProvider': 'rogw.tranp.semantics.provider.make_db',
		'rogw.tranp.semantics.reflections.Reflections': 'rogw.tranp.semantics.reflections.Reflections',
		'rogw.tranp.syntax.ast.resolver.SymbolMapping': 'rogw.tranp.providers.node.symbol_mapping',
		'rogw.tranp.syntax.ast.parser.ParserSetting': 'rogw.tranp.providers.ast.parser_setting',
		'rogw.tranp.syntax.ast.parser.SyntaxParser': 'rogw.tranp.implements.syntax.lark.parser.SyntaxParserOfLark',
	}
