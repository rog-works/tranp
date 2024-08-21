import json
from typing import IO, cast

import lark
from lark.indenter import PythonIndenter

from rogw.tranp.implements.syntax.lark.entry import EntryOfLark, Serialization
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting
from rogw.tranp.syntax.errors import SyntaxError


class SyntaxParserOfLark:
	"""シンタックスパーサー(Lark版)"""

	@injectable
	def __init__(self, loader: IFileLoader, setting: ParserSetting, caches: CacheProvider) -> None:
		"""インスタンスを生成

		Args:
			loader (IFileLoader): ファイルローダー @inject
			setting (ParserSetting): パーサー設定データ @inject
			caches (CacheProvider): キャッシュプロバイダー @inject
		"""
		self.__loader = loader
		self.__setting = setting
		self.__caches = caches

	@duck_typed
	def __call__(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		Note:
			@see syntax.ast.parser.SyntaxParser
		"""
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> lark.Lark:
		"""シンタックスパーサーをロード

		Returns:
			Lark: シンタックスパーサー
		"""
		def identity() -> dict[str, str]:
			return {
				'mtime': str(self.__loader.mtime(self.__setting.grammar)),
				'grammar': self.__setting.grammar,
				'start': self.__setting.start,
				'algorithem': self.__setting.algorithem,
			}

		@self.__caches.get('parser.cache', identity=identity(), format='bin')
		def instantiate() -> LarkStored:
			return LarkStored(lark.Lark(
				self.__loader.load(self.__setting.grammar),
				start=self.__setting.start,
				parser=self.__setting.algorithem,
				postlex=PythonIndenter(),
				propagate_positions=True
			))

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

		def source_path() -> str:
			return f'{basepath}.py'

		def identity() -> dict[str, str]:
			return {
				'grammar_mtime': str(self.__loader.mtime(self.__setting.grammar)),
				'mtime': str(self.__loader.mtime(source_path()))
			}

		def load_source() -> str:
			return self.__loader.load(source_path())

		@self.__caches.get(basepath, identity=identity(), format='json')
		def instantiate() -> EntryStored:
			try:
				return EntryStored(EntryOfLark(parser.parse(load_source())))
			except Exception as e:
				raise SyntaxError(f'file: {source_path()}') from e

		return instantiate().entry

	def dirty_get_origin(self) -> lark.Lark:
		"""Larkインスタンスを取得(デバッグ用)

		Returns:
			Lark: Larkインスタンス
		Note:
			デバッグ用途のため、基本的に使用しないことを推奨
		"""
		return self.__load_parser()


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
