from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSetting, SyntaxParser
from py2cpp.module.types import ModulePath


def parser_setting() -> ParserSetting:
	return ParserSetting(grammar='data/grammar.lark')


def make_entrypoint(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	return parser(module_path.actual)
