from py2cpp.lang.di import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	return {
		'py2cpp.ast.entry.Entry': 'py2cpp.ast.provider.make_entrypoint',
		'py2cpp.ast.query.Query': 'py2cpp.node.query.Nodes',
		'py2cpp.ast.resolver.SymbolMapping': 'py2cpp.node.provider.symbol_mapping',
		'py2cpp.ast.parser.ParserSettings': 'py2cpp.ast.provider.parser_settings',
		'py2cpp.ast.parser.SyntaxParser': 'py2cpp.tp_lark.parser.SyntaxParserOfLark',
		'py2cpp.lang.cache.CacheProvider': 'py2cpp.lang.cache.CacheProvider',
		'py2cpp.lang.cache.CacheSetting': 'py2cpp.ast.provider.cache_setting',
		'py2cpp.lang.io.FileLoader': 'py2cpp.lang.io.FileLoader',
		'py2cpp.module.types.LibraryPaths': 'py2cpp.module.provider.library_paths',
		'py2cpp.module.types.ModulePath': 'py2cpp.module.provider.module_path_dummy',
		'py2cpp.module.loader.ModuleLoader': 'py2cpp.module.provider.module_loader',
		'py2cpp.module.module.Module': 'py2cpp.module.module.Module',
		'py2cpp.module.modules.Modules': 'py2cpp.module.modules.Modules',
		'py2cpp.node.node.Node': 'py2cpp.node.provider.entrypoint',
		'py2cpp.node.resolver.NodeResolver': 'py2cpp.node.resolver.NodeResolver',
		'py2cpp.symbol.db.SymbolDB': 'py2cpp.symbol.db.SymbolDB',
		'py2cpp.symbol.symbols.Symbols': 'py2cpp.symbol.symbols.Symbols',
	}
