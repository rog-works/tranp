import hashlib
import json
from typing import Any, ClassVar, Self

from rogw.tranp.data.version import Versions
from rogw.tranp.errors import LogicError
from rogw.tranp.meta.types import ModuleMeta, TranslatorMeta


class MetaHeader:
	"""メタヘッダー"""

	Tag: ClassVar = '@tranp.meta'

	@classmethod
	def from_json(cls, json_str: str) -> Self:
		"""JSON文字列からインスタンスを復元

		Args:
			json_str (str): JSON文字列
		Returns:
			Self: インスタンス
		"""
		raw = json.loads(json_str)
		return cls(raw['module'], raw['translator'])

	def __init__(self, module_meta: ModuleMeta, translator_meta: TranslatorMeta) -> None:
		"""インスタンスを生成

		Args:
			module_meta (ModuleMeta): モジュールのメタ情報
			translator_meta (TranslatorMeta): トランスレーターのメタ情報
		"""
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
		return json.dumps({'version': Versions.app, 'module': self.module_meta, 'translator': self.translator_meta})

	def to_header_str(self) -> str:
		"""メタヘッダー文字列に変換

		Returns:
			str: メタヘッダー文字列
		"""
		return f'{self.Tag}: {self.to_json()}'
