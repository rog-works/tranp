from py2cpp.app.types import ModuleDefinitions


def default_definitions() -> ModuleDefinitions:
	return {
		'py2cpp.ast.entry.Entry': 'py2cpp.ast.provider.root',
		'py2cpp.ast.parser.FileLoader': 'py2cpp.ast.parser.FileLoader',
		'py2cpp.ast.parser.GrammarSettings': 'py2cpp.ast.provider.grammar_settings',
		'py2cpp.ast.parser.SyntaxParser': 'py2cpp.tp_lark.parser.SyntaxParserOfLark',
		'py2cpp.ast.query.Query': 'py2cpp.node.nodes.Nodes',
		'py2cpp.module.base.LibraryPaths': 'py2cpp.module.provider.library_paths',
		'py2cpp.module.base.ModulePath': 'py2cpp.module.provider.module_path_main',
		'py2cpp.module.loader.ModuleLoader': 'py2cpp.module.provider.module_loader',
		'py2cpp.module.module.Module': 'py2cpp.module.module.Module',
		'py2cpp.module.modules.Modules': 'py2cpp.module.modules.Modules',
		'py2cpp.node.classify.Classify': 'py2cpp.node.classify.Classify',
		'py2cpp.node.node.Node': 'py2cpp.node.provider.entrypoint',
		'py2cpp.node.nodes.Settings': 'py2cpp.node.provider.settings',
		'py2cpp.node.nodes.NodeResolver': 'py2cpp.node.nodes.NodeResolver',
		'py2cpp.node.symboldb.SymbolDB': 'py2cpp.node.symboldb.SymbolDB',
	}
