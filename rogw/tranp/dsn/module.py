from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.lang.annotation import override


class ModuleDSN:
	"""モジュールパスDSN"""

	@classmethod
	def full_joined(cls, *elems: str) -> str:
		"""要素を結合し、DSNを生成

		Args:
			*elems (str): 要素リスト
		Returns:
			str: DSN
		Note:
			### 注意事項
			* 必ずモジュールパスが先頭要素に入力されなければならない
			* 先頭要素にモジュールパスの区切り文字が存在する場合は後続要素を結合するのみ
		"""
		if elems[0].find('#') != -1:
			return DSN.join(*elems)

		return DSN.join(elems[0], cls.local_joined(*elems[1:]), delimiter='#')

	@classmethod
	def local_joined(cls, *local_elems: str) -> str:
		"""モジュール内のローカル要素を結合し、ローカルパスを生成

		Args:
			*local_elems (str): ローカル要素リスト
		Returns:
			str: ローカルパス
		"""
		return DSN.join(*local_elems)

	@classmethod
	def local_elem_counts(cls, dsn: str) -> int:
		"""DSNからローカル要素の数を算出

		Args:
			dsn (str): DSN
		Returns:
			int: ローカル要素の数
		"""
		_, local = cls.parsed(dsn) if dsn.find('#') != -1 else ('', dsn)
		return DSN.elem_counts(local)

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
		module_path, local = cls.parsed(dsn)
		return module_path, DSN.elements(local)

	@classmethod
	def identify(cls, dsn: str, id: int | str) -> str:
		"""IDを付与し、一意性を持ったDSNを生成

		Args:
			dsn (str): DSN
			id (int | str): ID
		Returns:
			str: DSN
		"""
		return DSN.identify(dsn, id)

	def __init__(self, dsn: str) -> None:
		"""インスタンスを生成

		Args:
			dsn (str): DSN
		"""
		module_path, local_path = self.parsed(dsn)
		self.dsn = self.full_joined(module_path, local_path)
		self.module_path = module_path
		self.local_path = local_path

	@property
	def locals(self) -> list[str]:
		"""list[str]: ローカル要素リスト"""
		return self.expanded(self.local_path)[1]

	@property
	def local_counts(self) -> int:
		"""int: ローカル要素の数"""
		return self.local_elem_counts(self.local_path)

	def join(self, *locals: str) -> 'ModuleDSN':
		"""現在のDSNにローカル要素を追加し、新たにDSNを生成

		Args:
			*locals (str): 追加するローカル要素リスト
		Returns:
			str: DSN
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
