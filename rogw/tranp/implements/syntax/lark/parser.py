import json
from typing import IO, cast

import lark
from lark.indenter import PythonIndenter

from rogw.tranp.implements.syntax.lark.entry import EntryOfLark, Serialization
from rogw.tranp.io.cache import CacheProvider, Stored
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceCodeProvider, SyntaxParser
from rogw.tranp.syntax.errors import SyntaxError


class SyntaxParserOfLark:
	"""シンタックスパーサー(Lark版)"""

	@injectable
	def __init__(self, loader: IFileLoader, codes: SourceCodeProvider, setting: ParserSetting, caches: CacheProvider) -> None:
		"""インスタンスを生成

		Args:
			loader (IFileLoader): ファイルローダー @inject
			codes (SourceCodeProvider): ソースコードプロバイダー @inject
			setting (ParserSetting): パーサー設定データ @inject
			caches (CacheProvider): キャッシュプロバイダー @inject
		"""
		self.__loader = loader
		self.__codes = codes
		self.__setting = setting
		self.__caches = caches

	@duck_typed(SyntaxParser)
	def __call__(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		"""
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> lark.Lark:
		"""シンタックスパーサーをロード

		Returns:
			Lark: シンタックスパーサー
		"""
		def handler() -> LarkStored:
			return LarkStored(lark.Lark(
				self.__loader.load(self.__setting.grammar),
				start=self.__setting.start,
				parser=self.__setting.algorithem,
				postlex=PythonIndenter(),
				propagate_positions=True
			))

		identity = {
			'mtime': str(self.__loader.mtime(self.__setting.grammar)),
			'grammar': self.__setting.grammar,
			'start': self.__setting.start,
			'algorithem': self.__setting.algorithem,
		}
		instantiate = self.__caches.get('parser.cache', identity=identity, format='bin')(handler)
		return instantiate().lark

	def __load_entry(self, parser: lark.Lark, module_path: str) -> Entry:
		"""シンタックスツリーをロード

		Args:
			parser (Lark): シンタックスパーサー
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		Raises:
			SyntaxError: ソースの解析に失敗
		"""
		basepath = module_path_to_filepath(module_path)
		source_path = f'{basepath}.py'

		# ストレージに存在しないモジュールはメモリ上に存在すると見做してキャッシュは省略
		if not self.__loader.exists(source_path):
			return EntryOfLark(parser.parse(self.__codes(module_path)))

		def handler() -> EntryStored:
			try:
				return EntryStored(EntryOfLark(parser.parse(self.__codes(module_path))))
			except Exception as e:
				raise SyntaxError(f'file: {source_path}') from e

		identity = {
			'grammar_mtime': str(self.__loader.mtime(self.__setting.grammar)),
			'mtime': str(self.__loader.mtime(source_path)),
		}
		instantiate = self.__caches.get(basepath, identity=identity, format='json')(handler)
		return instantiate().entry

	def dirty_get_origin(self) -> lark.Lark:
		"""Larkインスタンスを取得(デバッグ用)

		Returns:
			Lark: Larkインスタンス
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
			lark (Lark): Larkインスタンス
		"""
		self.lark = lark

	@classmethod
	def load(cls, stream: IO) -> 'LarkStored':
		""""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			LarkStored: インスタンス
		"""
		return LarkStored(lark.Lark.load(stream))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		self.lark.save(stream)


duck_typed(Stored)
class EntryStored:
	"""ストア(シンタックスツリー版)"""

	def __init__(self, entry: Entry) -> None:
		""""インスタンスを生成

		Args:
			lark (Lark): Larkインスタンス
		"""
		self.entry = entry

	@classmethod
	def load(cls, stream: IO) -> 'EntryStored':
		""""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			EntryStored: インスタンス
		"""
		data = json.load(stream)
		tree = cast(lark.Tree, Serialization.loads(data))
		return EntryStored(EntryOfLark(tree))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		data = Serialization.dumps(cast(lark.Tree, self.entry.source))
		stream.write(json.dumps(data, separators=(',', ':')).encode('utf-8'))
