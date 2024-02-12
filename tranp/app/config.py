from tranp.lang.di import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		ModuleDefinition: モジュール定義
	"""
	return {
		'tranp.analyze.db.SymbolDB': 'tranp.analyze.db.make_db',
		'tranp.analyze.finder.SymbolFinder': 'tranp.analyze.finder.SymbolFinder',
		'tranp.analyze.processor.Preprocessors': 'tranp.analyze.preprocessors.preprocessors',
		'tranp.analyze.symbols.Symbols': 'tranp.analyze.symbols.Symbols',
		'tranp.app.env.Env': 'tranp.providers.app.make_env',
		'tranp.ast.entry.Entry': 'tranp.providers.ast.make_entrypoint',
		'tranp.ast.query.Query': 'tranp.node.query.Nodes',
		'tranp.ast.resolver.SymbolMapping': 'tranp.providers.node.symbol_mapping',
		'tranp.ast.parser.ParserSetting': 'tranp.providers.ast.parser_setting',
		'tranp.ast.parser.SyntaxParser': 'tranp.tp_lark.parser.SyntaxParserOfLark',
		'tranp.io.cache.CacheProvider': 'tranp.io.cache.CacheProvider',
		'tranp.io.cache.CacheSetting': 'tranp.providers.io.cache_setting',
		'tranp.io.loader.FileLoader': 'tranp.io.loader.FileLoader',
		'tranp.module.loader.ModuleLoader': 'tranp.providers.module.module_loader',
		'tranp.module.module.Module': 'tranp.module.module.Module',
		'tranp.module.modules.Modules': 'tranp.module.modules.Modules',
		'tranp.module.types.LibraryPaths': 'tranp.providers.module.library_paths',
		'tranp.module.types.ModulePath': 'tranp.providers.module.module_path_dummy',
		'tranp.node.node.Node': 'tranp.providers.node.entrypoint',
		'tranp.node.resolver.NodeResolver': 'tranp.node.resolver.NodeResolver',
	}
