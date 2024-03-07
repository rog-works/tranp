import hashlib
import json
from typing import Any, ClassVar, Self

from rogw.tranp.data.meta.types import ModuleMeta, TranspilerMeta
from rogw.tranp.data.version import Versions
from rogw.tranp.errors import LogicError


class MetaHeader:
	"""メタヘッダー"""

	Tag: ClassVar = '@tranp.meta'

	@classmethod
	def try_from_content(cls, content: str) -> Self | None:
		"""テキストデータからインスタンスの復元を試行。メタヘッダーが存在しない場合はNoneを返却

		Args:
			content (str): テキストデータ
		Returns:
			Self | None: 復元したインスタンス。またはNone
		"""
		header_begin = content.find(MetaHeader.Tag)
		if header_begin == -1:
			return None

		json_begin = header_begin + len(MetaHeader.Tag) + 1
		json_end = content.find('\n', json_begin)
		return cls.from_json(content[json_begin:json_end])

	@classmethod
	def from_json(cls, json_str: str) -> Self:
		"""JSON文字列からインスタンスを復元

		Args:
			json_str (str): JSON文字列
		Returns:
			Self: 復元したインスタンス
		"""
		raw = json.loads(json_str)
		return cls(raw['module'], raw['transpiler'], raw['version'])

	def __init__(self, module_meta: ModuleMeta, translator_meta: TranspilerMeta, app_version: str | None = None) -> None:
		"""インスタンスを生成

		Args:
			module_meta (ModuleMeta): モジュールのメタ情報
			translator_meta (TranspilerMeta): トランスパイラーのメタ情報
			app_version (str | None): アプリケーションバージョン (default = None)
		"""
		self.app_version = app_version or Versions.app
		self.module_meta = module_meta
		self.translator_meta = translator_meta

	@property
	def identity(self) -> str:
		"""str: 一意な識別子"""
		return hashlib.md5(self.to_json().encode('utf-8')).hexdigest()

	def __eq__(self, other: Any) -> bool:
		"""比較演算子のおバーロード
		
		Args:
			other (Any): 比較対象
		Returns:
			bool: True = 一致
		Raises:
			LogicError: 同種以外のインスタンスを指定
		"""
		if type(other) is not MetaHeader:
			raise LogicError(f'Not allowed comparison. other: {type(other)}')

		return self.identity == other.identity

	def to_json(self) -> str:
		"""JSONにシリアライズ

		Returns:
			str: JSON文字列
		"""
		return json.dumps({'version': self.app_version, 'module': self.module_meta, 'transpiler': self.translator_meta}, separators=(',', ':'))

	def to_header_str(self) -> str:
		"""メタヘッダー文字列に変換

		Returns:
			str: メタヘッダー文字列
		"""
		return f'{self.Tag}: {self.to_json()}'
