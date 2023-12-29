from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import GrammarSettings, SyntaxParser
from py2cpp.module.base import ModulePath


def grammar_settings() -> GrammarSettings:
	return GrammarSettings(grammar='data/grammar.lark')


def make_entrypoint(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	return parser.parse(module_path)
