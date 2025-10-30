import json
from typing import IO, cast

import lark
from lark.indenter import PythonIndenter

from rogw.tranp.cache.cache import CacheProvider, Stored
from rogw.tranp.errors import Errors
from rogw.tranp.file.loader import IDataLoader, ISourceLoader
from rogw.tranp.implements.syntax.lark.entry import EntryOfLark, Serialization
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceProvider, SyntaxParser


class SyntaxParserOfLark:
	"""シンタックスパーサー(Lark版)"""

	@injectable
	def __init__(self, datums: IDataLoader, sources: ISourceLoader, source_provider: SourceProvider, setting: ParserSetting, caches: CacheProvider) -> None:
		"""インスタンスを生成

		Args:
			datums: データローダー @inject
			sources: ソースコードローダー @inject
			source_provider: ソースコードプロバイダー @inject
			setting: パーサー設定データ @inject
			caches: キャッシュプロバイダー @inject
		"""
		self.__datums = datums
		self.__sources = sources
		self.__source_provider = source_provider
		self.__setting = setting
		self.__caches = caches

	@duck_typed(SyntaxParser)
	def __call__(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path: モジュールパス
		Returns:
			シンタックスツリーのルートエントリー
		"""
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> lark.Lark:
		"""シンタックスパーサーをロード

		Returns:
			シンタックスパーサー
		"""
		def instantiate() -> LarkStored:
			return LarkStored(lark.Lark(
				self.__datums.load(self.__setting.grammar),
				start=self.__setting.start,
				parser=self.__setting.algorithem,
				postlex=PythonIndenter(),
				propagate_positions=True
			))

		identity = {
			'mtime': str(self.__datums.mtime(self.__setting.grammar)),
			'grammar': self.__setting.grammar,
			'start': self.__setting.start,
			'algorithem': self.__setting.algorithem,
		}
		decorator = self.__caches.get('parser.cache', identity=identity, format='bin')
		return decorator(instantiate)().lark

	def __load_entry(self, parser: lark.Lark, module_path: str) -> Entry:
		"""シンタックスツリーをロード

		Args:
			parser: シンタックスパーサー
			module_path: モジュールパス
		Returns:
			シンタックスツリーのルートエントリー
		Raises:
			Errors.Syntax: ソースの解析に失敗
		"""
		basepath = module_path_to_filepath(module_path)
		source_path = f'{basepath}.py'

		# ストレージに存在しないモジュールはメモリ上に存在すると見做して毎回パース
		if not self.__sources.exists(source_path):
			return EntryOfLark(parser.parse(self.__source_provider(module_path)))

		def instantiate() -> EntryStored:
			try:
				return EntryStored(EntryOfLark(parser.parse(self.__source_provider(module_path))))
			except Exception as e:
				raise Errors.Syntax(source_path, e) from e

		identity = {
			'grammar_mtime': str(self.__datums.mtime(self.__setting.grammar)),
			'mtime': str(self.__sources.mtime(source_path)),
		}
		decorator = self.__caches.get(basepath, identity=identity, format='json')
		return decorator(instantiate)().entry

	def dirty_get_origin(self) -> lark.Lark:
		"""Larkインスタンスを取得(デバッグ用)

		Returns:
			Larkインスタンス
		Note:
			デバッグ用途のため、基本的に使用しないことを推奨
		"""
		return self.__load_parser()


duck_typed(Stored)
class LarkStored:
	"""ストア(Lark版)"""

	def __init__(self, lark: lark.Lark) -> None:
		""""インスタンスを生成

		Args:
			lark: Larkインスタンス
		"""
		self.lark = lark

	@classmethod
	def load(cls, stream: IO) -> 'LarkStored':
		""""インスタンスを復元

		Args:
			stream: IO
		Returns:
			インスタンス
		"""
		return LarkStored(lark.Lark.load(stream))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream: IO
		"""
		self.lark.save(stream)


duck_typed(Stored)
class EntryStored:
	"""ストア(シンタックスツリー版)"""

	def __init__(self, entry: Entry) -> None:
		""""インスタンスを生成

		Args:
			lark: Larkインスタンス
		"""
		self.entry = entry

	@classmethod
	def load(cls, stream: IO) -> 'EntryStored':
		""""インスタンスを復元

		Args:
			stream: IO
		Returns:
			インスタンス
		"""
		data = json.load(stream)
		tree = cast(lark.Tree, Serialization.loads(data))
		return EntryStored(EntryOfLark(tree))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream: IO
		"""
		data = Serialization.dumps(cast(lark.Tree, self.entry.source))
		stream.write(json.dumps(data, separators=(',', ':')).encode('utf-8'))
