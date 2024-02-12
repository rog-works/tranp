from tranp.ast.entry import Entry
from tranp.ast.parser import ParserSetting, SyntaxParser
from tranp.module.types import ModulePath


def parser_setting() -> ParserSetting:
	return ParserSetting(grammar='data/grammar.lark')


def make_entrypoint(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	return parser(module_path.actual)
