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
			content: テキストデータ
		Returns:
			復元したインスタンス。またはNone
		"""
		header_begin = content.find(MetaHeader.Tag)
		if header_begin == -1:
			return None

		json_begin = header_begin + len(MetaHeader.Tag) + 1
		line_break = content.find('\n', json_begin)
		json_end = content.rfind('}', json_begin, line_break) + 1
		return cls.from_json(content[json_begin:json_end])

	@classmethod
	def from_json(cls, json_str: str) -> Self:
		"""JSON文字列からインスタンスを復元

		Args:
			json_str: JSON文字列
		Returns:
			復元したインスタンス
		"""
		raw = json.loads(json_str)
		return cls(raw['module'], raw['transpiler'], raw['version'])

	def __init__(self, module_meta: ModuleMeta, transpiler_meta: TranspilerMeta, app_version: str | None = None) -> None:
		"""インスタンスを生成

		Args:
			module_meta: モジュールのメタ情報
			transpiler_meta: トランスパイラーのメタ情報
			app_version: アプリケーションバージョン (default = None)
		"""
		self.app_version = app_version or Versions.app
		self.module_meta = module_meta
		self.transpiler_meta = transpiler_meta

	@property
	def identity(self) -> str:
		"""Returns: 一意な識別子"""
		return hashlib.md5(self.to_json().encode('utf-8')).hexdigest()

	def __eq__(self, other: Any) -> bool:
		"""比較演算子のオーバーロード
		
		Args:
			other: 比較対象
		Returns:
			True = 一致
		Raises:
			LogicError: 同種以外のインスタンスを指定
		"""
		if type(other) is not MetaHeader:
			raise LogicError(f'Not allowed comparison. other: {type(other)}')

		return self.identity == other.identity

	def to_json(self) -> str:
		"""JSONにシリアライズ

		Returns:
			JSON文字列
		"""
		return json.dumps({'version': self.app_version, 'module': self.module_meta, 'transpiler': self.transpiler_meta}, separators=(',', ':'))

	def to_header_str(self) -> str:
		"""メタヘッダー文字列に変換

		Returns:
			メタヘッダー文字列
		"""
		return f'{self.Tag}: {self.to_json()}'
