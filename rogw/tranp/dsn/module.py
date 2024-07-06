from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.lang.annotation import override


class ModuleDSN:
	"""モジュールパスDSN

	Note:
		* モジュールパスとローカルパスを結合した文字列
		* モジュールパスとローカルパスの区切り文字は`#`
		* それ以外の区切り文字は`.`
		例: `module.path.to#local.symbol`
	"""

	@classmethod
	def full_join(cls, dsn: str, *elems: str) -> 'ModuleDSN':
		"""要素を結合し、DSNを生成

		Args:
			dsn (str): DSN
			*elems (str): ローカル要素リスト
		Returns:
			ModuleDSN: 生成したインスタンス
		Note:
			@see full_joined
		"""
		return cls(cls.full_joined(dsn, *elems))

	@classmethod
	def full_joined(cls, dsn: str, *elems: str) -> str:
		"""要素を結合し、DSNを生成

		Args:
			dsn (str): DSN
			*elems (str): ローカル要素リスト
		Returns:
			str: DSN
		Note:
			### 注意事項
			* 先頭要素に必ずモジュールパスを含めること
			* 先頭要素にモジュールパスの区切り文字が存在する場合は後続要素を結合するのみ
		"""
		if dsn.find('#') != -1:
			return DSN.join(dsn, *elems)

		return DSN.join(dsn, cls.local_joined(*elems), delimiter='#')

	@classmethod
	def local_joined(cls, *elems: str) -> str:
		"""モジュール内のローカル要素を結合し、ローカルパスを生成

		Args:
			*elems (str): ローカル要素リスト
		Returns:
			str: ローカルパス
		Note:
			このメソッドの返却値はローカルパスであり、モジュールDSNではない点に注意
		"""
		return DSN.join(*elems)

	@classmethod
	def expand_elements(cls, dsn_or_local: str) -> list[str]:
		"""DSNまたはローカルパスからローカル要素を分解

		Args:
			dsn_or_local (str): DSNまたはローカルパス
		Returns:
			list[str]: ローカル要素リスト
		"""
		_, local = cls.parsed(dsn_or_local) if dsn_or_local.find('#') != -1 else ('', dsn_or_local)
		return DSN.elements(local)

	@classmethod
	def local_elem_counts(cls, dsn_or_local: str) -> int:
		"""DSNまたはローカルパスに含まれるローカル要素の数を算出

		Args:
			dsn_or_local (str): DSNまたはローカルパス
		Returns:
			int: ローカル要素の数
		"""
		return len(cls.expand_elements(dsn_or_local))

	@classmethod
	def parsed(cls, dsn: str) -> tuple[str, str]:
		"""DSNを解析し、モジュールパスとローカルパスに分離

		Args:
			dsn (str): DSN
		Returns:
			tuple[str, str]: (モジュールパス, ローカルパス)
		"""
		elems = dsn.split('#')
		return (elems[0], elems[1]) if len(elems) > 1 else (elems[0], '')

	@classmethod
	def expanded(cls, dsn: str) -> tuple[str, list[str]]:
		"""DSNを解析し、モジュールパスとローカル要素に分離

		Args:
			dsn (str): DSN
		Returns:
			tuple[str, list[str]]: (モジュールパス, ローカル要素リスト)
		"""
		module_path, local_path = cls.parsed(dsn)
		return module_path, DSN.elements(local_path)

	@classmethod
	def identify(cls, dsn: str, id: int | str) -> str:
		"""IDを付与し、一意性を持ったDSNを生成

		Args:
			dsn (str): DSN
			id (int | str): ID
		Returns:
			str: DSN
		"""
		return f'{dsn}@{id}'

	def __init__(self, dsn: str) -> None:
		"""インスタンスを生成

		Args:
			dsn (str): DSN
		"""
		module_path, local_path = self.parsed(dsn)
		self.dsn = dsn
		self.module_path = module_path
		self.local_path = local_path

	@property
	def elements(self) -> list[str]:
		"""list[str]: ローカル要素リスト"""
		return self.expand_elements(self.local_path)

	@property
	def elem_counts(self) -> int:
		"""int: ローカル要素の数"""
		return self.local_elem_counts(self.local_path)

	def join(self, *locals: str) -> 'ModuleDSN':
		"""DSNの末尾にローカル要素を追加し、新たにDSNを生成

		Args:
			*locals (str): 追加するローカル要素リスト
		Returns:
			ModuleDSN: 生成したインスタンス
		"""
		return self.__class__(self.full_joined(self.dsn, *locals))

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.dsn}>'

	@override
	def __hash__(self) -> int:
		"""int: オブジェクトのハッシュ値"""
		return hash(self.__repr__())
