import re

from rogw.tranp.syntax.ast.dsn import DSN
from rogw.tranp.errors import LogicError


class EntryPath:
	"""エントリーパス"""

	@classmethod
	def join(cls, *elems: str) -> 'EntryPath':
		"""要素を結合してインスタンスを生成

		Args:
			*elems (str): 要素リスト
		Returns:
			EntryPath: インスタンス
		"""
		return cls(DSN.join(*elems))

	@classmethod
	def identify(cls, origin: str, entry_tag: str, index: int) -> 'EntryPath':
		"""一意性を持つようにパスを構築し、インスタンスを生成

		Args:
			origin (str): パス
			entry_tag (str): エントリータグ
			index (int): 要素インデックス
		Returns:
			EntryPath: インスタンス
		"""
		return cls(DSN.join(*[origin, f'{entry_tag}[{index}]']))

	def __init__(self, origin: str) -> None:
		"""インスタンスを生成

		Args:
			origin (str): パス
		"""
		self.origin = origin

	@property
	def valid(self) -> bool:
		"""bool: True = パスが有効"""
		return DSN.elem_counts(self.origin) > 0

	@property
	def elements(self) -> list[str]:
		"""list[str]: 区切り文字で分解した要素を返却"""
		return DSN.elements(self.origin)

	@property
	def escaped_origin(self) -> str:
		"""str: 正規表現用にエスケープしたパスを返却"""
		return re.sub(r'([.\[\]])', r'\\\1', self.origin)

	def joined(self, relative: str) -> str:
		"""相対パスと連結したパスを返却

		Args:
			relative (str): 相対パス
		Returns:
			str: パス
		"""
		return DSN.join(*[self.origin, relative])

	@property
	def first(self) -> tuple[str, int]:
		"""先頭の要素を分解して取得

		Returns:
			tuple[str, int]: (エントリータグ, 要素インデックス)
		"""
		return self.__break_tag(self.elements[0])

	@property
	def last(self) -> tuple[str, int]:
		"""末尾の要素を分解して取得

		Returns:
			tuple[str, int]: (エントリータグ, 要素インデックス)
		"""
		return self.__break_tag(self.elements[-1])

	@property
	def first_tag(self) -> str:
		"""先頭のエントリータグを取得

		Returns:
			str: エントリータグ
		"""
		return self.first[0]

	@property
	def last_tag(self) -> str:
		"""末尾のエントリータグを取得

		Returns:
			str: エントリータグ
		"""
		return self.last[0]

	@property
	def parent_tag(self) -> str:
		"""親のエントリータグを取得

		Returns:
			str: エントリータグ
		"""
		return self.shift(-1).last[0]

	def __break_tag(self, elem: str) -> tuple[str, int]:
		"""要素から元のタグと付与されたインデックスに分解。インデックスがない場合は-1とする

		Args:
			elem (str): 要素
		Returns:
			tuple[str, int]: (エントリータグ, インデックス)
		"""
		if not elem.endswith(']'):
			return (elem, -1)

		before, after = elem.split('[')
		return (before, int(after[:-1]))

	def contains(self, entry_tag: str) -> bool:
		"""指定のエントリータグが含まれるか判定

		Args:
			entry_tag (str): エントリータグ
		Returns:
			bool: True = 含まれる
		"""
		return entry_tag in self.de_identify().elements

	def consists_of_only(self, *entry_tags: str) -> bool:
		"""指定のエントリータグのみでパスが構築されているか判定

		Args:
			*entry_tags (str): エントリータグリスト
		Returns:
			bool: True = 構築されている
		"""
		return len([entry_tag for entry_tag in self.de_identify().elements if entry_tag not in entry_tags]) == 0

	def de_identify(self) -> 'EntryPath':
		"""一意性を解除したパスでインスタンスを生成

		Returns:
			EntryPath: インスタンス
		"""
		return EntryPath(re.sub(r'\[\d+\]', '', self.origin))

	def relativefy(self, starts: str) -> 'EntryPath':
		"""指定のパスより先の相対パスでインスタンスを生成

		Args:
			starts (str): 先頭のパス
		Returns:
			EntryPath: インスタンス
		Raises:
			LogicError: 一致しない先頭パスを指定
		"""
		if not self.origin.startswith(f'{starts}.'):
			raise LogicError(self, starts)

		return EntryPath(DSN.relativefy(self.origin, starts))

	def shift(self, skip: int) -> 'EntryPath':
		"""指定方向の要素を除外して再構築したパスでインスタンスを生成

		Args:
			skip (int): 移動方向
		Returns:
			EntryPath: インスタンス
		"""
		elems = self.elements
		if skip == 0:
			pass
		elif skip > 0:
			elems = elems[skip:]
		elif skip < 1:
			elems = elems[:skip]

		return self.join(*elems)
