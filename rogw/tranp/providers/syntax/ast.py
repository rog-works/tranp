from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceCodeProvider, SyntaxParser


def parser_setting() -> ParserSetting:
	"""シンタックスパーサー設定データを生成

	Returns:
		ParserSettind: シンタックスパーサー設定データ
	"""
	return ParserSetting(grammar='data/grammar.lark')


@injectable
def source_code_provider(loader: IFileLoader) -> SourceCodeProvider:
	"""ソースコードプロバイダーを生成

	Args:
		loader (IFileLoader): ファイルローダー @inject
	Returns:
		SourceCodeProvider: ソースコードプロバイダー
	"""
	return lambda module_path: loader.load(module_path_to_filepath(module_path, '.py'))


@injectable
def make_root_entry(module_path: ModulePath, parser: SyntaxParser) -> Entry:
	"""ASTのルート要素を生成

	Args:
		module_path (ModulePath): モジュールパス @inject
		parser (SyntaxParser): シンタックスパーサー @inject
	Returns:
		Entry: ASTのルート要素
	"""
	return parser(module_path.path)
