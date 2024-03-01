from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SyntaxParser


def parser_setting() -> ParserSetting:
	"""シンタックスパーサー設定データを生成

	Returns:
		ParserSettind: シンタックスパーサー設定データ
	"""
	return ParserSetting(grammar='data/grammar.lark')


def make_entrypoint(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	"""ASTのルート要素を生成

	Args:
		module_path (ModulePath): モジュールパス
		parser (SyntaxParser): シンタックスパーサー
	Returns:
		Entry: ASTのルート要素
	"""
	return parser(module_path.actual)
