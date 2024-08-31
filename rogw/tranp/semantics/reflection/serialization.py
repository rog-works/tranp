from abc import ABCMeta, abstractmethod
from typing import Literal, MutableMapping, TypedDict

from rogw.tranp.semantics.reflection.base import IReflection

DictSymbol = TypedDict('DictSymbol', {'class': Literal['Symbol'], 'types': str, 'attrs': dict[str, str]})
DictReflection = TypedDict('DictReflection', {'class': Literal['Reflection'], 'node': str, 'decl': str, 'origin': str, 'via': str, 'attrs': dict[str, str]})
DictSerialized = DictSymbol | DictReflection


class IReflectionSerializer(metaclass=ABCMeta):
	"""シンボルシリアライザー"""

	@abstractmethod
	def serialize(self, symbol: IReflection) -> DictSerialized:
		"""シリアライズ

		Args:
			symbol (IReflection): シンボル
		Returns:
			dict[str, Any]: データ
		"""
		...

	@abstractmethod
	def deserialize(self, db: MutableMapping[str, IReflection], data: DictSerialized) -> IReflection:
		"""デシリアライズ

		Args:
			db (MutableMapping[str, IReflection]): シンボルテーブル
			data (dict[str, Any]): データ
		Returns:
			IReflection: シンボル
		"""
		...
