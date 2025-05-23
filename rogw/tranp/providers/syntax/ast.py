from rogw.tranp.file.loader import ISourceLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceProvider, SyntaxParser


def parser_setting() -> ParserSetting:
	"""シンタックスパーサー設定データを生成

	Returns:
		シンタックスパーサー設定データ
	"""
	return ParserSetting(grammar='data/grammar.lark')


@injectable
def source_provider(sources: ISourceLoader) -> SourceProvider:
	"""ソースコードプロバイダーを生成

	Args:
		sources: ソースコードローダー @inject
	Returns:
		ソースコードプロバイダー
	"""
	return lambda module_path: sources.load(module_path_to_filepath(module_path, '.py'))


@injectable
def make_root_entry(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	"""ASTのルート要素を生成

	Args:
		module_path: モジュールパス @inject
		parser: シンタックスパーサー @inject
	Returns:
		ASTのルート要素
	"""
	return parser(module_path.path)
