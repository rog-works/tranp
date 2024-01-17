from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSetting, SyntaxParser
from py2cpp.lang.cache import CacheSetting
from py2cpp.module.types import ModulePath


def cache_setting() -> CacheSetting:
	return CacheSetting(basedir='.cache/py2cpp')


def parser_setting() -> ParserSetting:
	return ParserSetting(grammar='data/grammar.lark')


def make_entrypoint(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	return parser(module_path.actual)
