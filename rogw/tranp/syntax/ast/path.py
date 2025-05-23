import re

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import LogicError


class EntryPath:
	"""エントリーパス"""

	@classmethod
	def join(cls, *elems: str) -> 'EntryPath':
		"""要素を結合してインスタンスを生成

		Args:
			*elems: 要素リスト
		Returns:
			インスタンス
		"""
		return cls(DSN.join(*elems))

	@classmethod
	def identify(cls, origin: str, entry_tag: str, index: int) -> 'EntryPath':
		"""一意性を持つようにパスを構築し、インスタンスを生成

		Args:
			origin: パス
			entry_tag: エントリータグ
			index: 要素インデックス
		Returns:
			インスタンス
		"""
		return cls(DSN.join(*[origin, f'{entry_tag}[{index}]']))

	def __init__(self, origin: str) -> None:
		"""インスタンスを生成

		Args:
			origin: パス
		"""
		self.origin = origin

	@property
	def valid(self) -> bool:
		"""Returns: True = パスが有効"""
		return DSN.elem_counts(self.origin) > 0

	@property
	def elements(self) -> list[str]:
		"""Returns: 区切り文字で分解した要素を返却"""
		return DSN.elements(self.origin)

	@property
	def escaped_origin(self) -> str:
		"""Returns: 正規表現用にエスケープしたパスを返却"""
		return ''.join([f'\\{c}' if c in '.[]' else c for c in self.origin])

	def joined(self, relative: str) -> str:
		"""相対パスと連結したパスを返却

		Args:
			relative: 相対パス
		Returns:
			パス
		"""
		return DSN.join(*[self.origin, relative])

	@property
	def first(self) -> tuple[str, int]:
		"""先頭の要素を分解して取得

		Returns:
			(エントリータグ, 要素インデックス)
		"""
		return self.__break_tag(self.elements[0])

	@property
	def last(self) -> tuple[str, int]:
		"""末尾の要素を分解して取得

		Returns:
			(エントリータグ, 要素インデックス)
		"""
		return self.__break_tag(self.elements[-1])

	@property
	def first_tag(self) -> str:
		"""先頭のエントリータグを取得

		Returns:
			エントリータグ
		"""
		return self.first[0]

	@property
	def last_tag(self) -> str:
		"""末尾のエントリータグを取得

		Returns:
			エントリータグ
		"""
		return self.last[0]

	@property
	def parent_tag(self) -> str:
		"""親のエントリータグを取得

		Returns:
			エントリータグ
		"""
		return self.shift(-1).last[0]

	def __break_tag(self, elem: str) -> tuple[str, int]:
		"""要素から元のタグと付与されたインデックスに分解。インデックスがない場合は-1とする

		Args:
			elem: 要素
		Returns:
			(エントリータグ, インデックス)
		"""
		if not elem.endswith(']'):
			return (elem, -1)

		before, after = elem.split('[')
		return (before, int(after[:-1]))

	def contains(self, entry_tag: str) -> bool:
		"""指定のエントリータグが含まれるか判定

		Args:
			entry_tag: エントリータグ
		Returns:
			True = 含まれる
		"""
		return entry_tag in self.de_identify().elements

	def consists_of_only(self, *entry_tags: str) -> bool:
		"""指定のエントリータグのみでパスが構築されているか判定

		Args:
			*entry_tags: エントリータグリスト
		Returns:
			True = 構築されている
		"""
		return len([entry_tag for entry_tag in self.de_identify().elements if entry_tag not in entry_tags]) == 0

	def de_identify(self) -> 'EntryPath':
		"""一意性を解除したパスでインスタンスを生成

		Returns:
			インスタンス
		"""
		de_origin = re.sub(r'\[\d+\]', '', self.origin)
		return EntryPath(de_origin)

	def relativefy(self, starts: str) -> 'EntryPath':
		"""指定のパスより先の相対パスでインスタンスを生成

		Args:
			starts: 先頭のパス
		Returns:
			インスタンス
		Raises:
			LogicError: 一致しない先頭パスを指定
		"""
		if not self.origin.startswith(f'{starts}.'):
			raise LogicError(self, starts)

		return EntryPath(DSN.relativefy(self.origin, starts))

	def shift(self, skip: int) -> 'EntryPath':
		"""指定方向の要素を除外して再構築したパスでインスタンスを生成

		Args:
			skip: 移動方向
		Returns:
			インスタンス
		"""
		elems = self.elements
		if skip == 0:
			pass
		elif skip > 0:
			elems = elems[skip:]
		elif skip < 1:
			elems = elems[:skip]

		return self.join(*elems)
