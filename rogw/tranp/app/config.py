from rogw.tranp.lang.di import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		ModuleDefinition: モジュール定義
	"""
	return {
		'rogw.tranp.semantics.db.SymbolDB': 'rogw.tranp.semantics.db.make_db',
		'rogw.tranp.semantics.finder.SymbolFinder': 'rogw.tranp.semantics.finder.SymbolFinder',
		'rogw.tranp.semantics.plugin.PluginProvider': 'rogw.tranp.providers.analyze.plugin_provider',
		'rogw.tranp.semantics.processor.Preprocessors': 'rogw.tranp.semantics.preprocessors.preprocessors',
		'rogw.tranp.semantics.symbols.Symbols': 'rogw.tranp.semantics.symbols.Symbols',
		'rogw.tranp.app.env.Env': 'rogw.tranp.providers.app.make_env',
		'rogw.tranp.ast.entry.Entry': 'rogw.tranp.providers.ast.make_entrypoint',
		'rogw.tranp.ast.query.Query': 'rogw.tranp.node.query.Nodes',
		'rogw.tranp.ast.resolver.SymbolMapping': 'rogw.tranp.providers.node.symbol_mapping',
		'rogw.tranp.ast.parser.ParserSetting': 'rogw.tranp.providers.ast.parser_setting',
		'rogw.tranp.ast.parser.SyntaxParser': 'rogw.tranp.tp_lark.parser.SyntaxParserOfLark',
		'rogw.tranp.i18n.i18n.I18n': 'rogw.tranp.i18n.i18n.I18n',
		'rogw.tranp.i18n.i18n.TranslationMapping': 'rogw.tranp.i18n.i18n.translation_mapping_empty',
		'rogw.tranp.io.cache.CacheProvider': 'rogw.tranp.io.cache.CacheProvider',
		'rogw.tranp.io.cache.CacheSetting': 'rogw.tranp.providers.io.cache_setting',
		'rogw.tranp.io.loader.IFileLoader': 'rogw.tranp.app.io.FileLoader',
		'rogw.tranp.module.loader.ModuleLoader': 'rogw.tranp.providers.module.module_loader',
		'rogw.tranp.module.module.Module': 'rogw.tranp.module.module.Module',
		'rogw.tranp.module.modules.Modules': 'rogw.tranp.module.modules.Modules',
		'rogw.tranp.module.types.LibraryPaths': 'rogw.tranp.providers.module.library_paths',
		'rogw.tranp.module.types.ModulePath': 'rogw.tranp.providers.module.module_path_dummy',
		'rogw.tranp.node.node.Node': 'rogw.tranp.providers.node.entrypoint',
		'rogw.tranp.node.resolver.NodeResolver': 'rogw.tranp.node.resolver.NodeResolver',
	}
