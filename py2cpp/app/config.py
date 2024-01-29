from py2cpp.lang.di import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	"""デフォルトのモジュール定義を取得

	Returns:
		ModuleDefinition: モジュール定義
	"""
	return {
		'py2cpp.analize.db.SymbolDB': 'py2cpp.analize.db.SymbolDB',
		'py2cpp.analize.processor.Preprocessors': 'py2cpp.providers.analyze.preprocessors',
		'py2cpp.analize.symbols.Symbols': 'py2cpp.analize.symbols.Symbols',
		'py2cpp.app.env.Env': 'py2cpp.providers.app.make_env',
		'py2cpp.ast.entry.Entry': 'py2cpp.providers.ast.make_entrypoint',
		'py2cpp.ast.query.Query': 'py2cpp.node.query.Nodes',
		'py2cpp.ast.resolver.SymbolMapping': 'py2cpp.providers.node.symbol_mapping',
		'py2cpp.ast.parser.ParserSetting': 'py2cpp.providers.ast.parser_setting',
		'py2cpp.ast.parser.SyntaxParser': 'py2cpp.tp_lark.parser.SyntaxParserOfLark',
		'py2cpp.io.cache.CacheProvider': 'py2cpp.io.cache.CacheProvider',
		'py2cpp.io.cache.CacheSetting': 'py2cpp.providers.io.cache_setting',
		'py2cpp.io.loader.FileLoader': 'py2cpp.io.loader.FileLoader',
		'py2cpp.module.loader.ModuleLoader': 'py2cpp.providers.module.module_loader',
		'py2cpp.module.module.Module': 'py2cpp.module.module.Module',
		'py2cpp.module.modules.Modules': 'py2cpp.module.modules.Modules',
		'py2cpp.module.types.LibraryPaths': 'py2cpp.providers.module.library_paths',
		'py2cpp.module.types.ModulePath': 'py2cpp.providers.module.module_path_dummy',
		'py2cpp.node.node.Node': 'py2cpp.providers.node.entrypoint',
		'py2cpp.node.resolver.NodeResolver': 'py2cpp.node.resolver.NodeResolver',
	}
