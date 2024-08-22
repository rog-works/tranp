from rogw.tranp.semantics.reflection.interface import IReflection


class IObject:
	"""拡張インターフェイス(オブジェクト)"""

	def prop_of(self, name: str) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			name (str): 名前
		Returns:
			IReflection: シンボル
		"""
		...
