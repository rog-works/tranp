from enum import Enum
from typing import Callable, Iterator


class BlockParser:
	"""ブロックパーサー"""

	_all_pair = ['[]', '()', '{}', '<>', '""', "''"]

	class Kinds(Enum):
		"""エントリーの種別"""
		Element = 'element'
		Block = 'block'
		End = 'end'

	class Entry:
		"""エントリー"""

		def __init__(self, begin: int, end: int, depth: int, kind: 'BlockParser.Kinds', entries: list['BlockParser.Entry']) -> None:
			"""インスタンスを生成

			Args:
				begin (int): 開始位置
				end (int): 終了位置
				depth (int): 深度
				kind (Kinds): エントリーの種別
				entries (Entry): 配下のエントリーリスト
			"""
			self.begin = begin
			self.end = end
			self.depth = depth
			self.kind = kind
			self.entries = entries

		def unders(self) -> Iterator['BlockParser.Entry']:
			"""配下の全エントリーを取得

			Args:
				Iterator[Entry]: エントリー
			"""
			for entry in self.entries:
				yield entry

				for in_entry in entry.entries:
					yield in_entry

	@classmethod
	def parse(cls, text: str, brackets: str = '()', delimiter: str = ',') -> 'BlockParser.Entry':
		"""ブロックを表す文字列を解析。ブロックと要素をエントリーとして分解し、ルートのエントリーを返却

		Args:
			text (str): 解析対象の文字列
			brackets (str): 括弧のペア (default = '()')
			delimiter (str): 区切り文字 (default = ',')
		Returns:
			Entry: エントリー
		"""
		return cls._parse(text, brackets, delimiter, 0, 0)[1][0]

	@classmethod
	def _parse(cls, text: str, brackets: str, delimiter: str, begin: int, depth: int) -> tuple[int, list['BlockParser.Entry']]:
		"""ブロックを表す文字列を解析。ブロックと要素をエントリーとして分解し、エントリーリストを返却

		Args:
			text (str): 解析対象の文字列
			brackets (str): 括弧のペア
			delimiter (str): 区切り文字
			begin (int): 開始位置
			depth (int): 深度
		Returns:
			tuple[int, list[Entry]]: (読み取り終了位置, エントリーのリスト)
		"""
		index = begin
		entries: list[BlockParser.Entry] = []
		while index < len(text):
			kind, entry_begin, pos_for_kind = cls._analyze_entry(text, brackets, delimiter, index)
			index = entry_begin
			if kind == cls.Kinds.Block:
				end, in_entries = cls._parse_block(text, brackets, delimiter, pos_for_kind + 1, depth)
				entries.append(cls.Entry(index, end, depth, kind, in_entries))
				index = end + 1
			elif kind == cls.Kinds.Element:
				entries.append(cls.Entry(index, pos_for_kind, depth, kind, []))
				index = pos_for_kind
			else:
				break

		return index, entries

	@classmethod
	def _analyze_entry(cls, text: str, brackets: str, delimiter: str, begin: int) -> tuple[Kinds, int, int]:
		"""エントリーの開始位置/種別を解析

		Args:
			text (str): 解析対象の文字列
			brackets (str): 括弧のペア
			delimiter (str): 区切り文字
			begin (int): 開始位置
		Returns:
			tuple[Kinds, int, int]: (エントリーの種別, エントリーの開始位置, ブロックの開始位置/要素の終了位置)
		"""
		index = begin
		if text[index] == brackets[0]:
			return cls.Kinds.Block, index, index
		elif text[index] == brackets[1]:
			return cls.Kinds.End, index, -1

		if text[index] in delimiter:
			index += 1

		entry_begin = index
		end_tokens_of_element = f'{brackets}{delimiter}'
		other_tokens = ''.join([pair for pair in cls._all_pair if pair != brackets])
		while index < len(text):
			if text[index] in other_tokens:
				index = cls._skip_other_block(text, other_tokens, index)
				continue

			if text[index] == brackets[0]:
				return cls.Kinds.Block, entry_begin, index
			elif text[index] in end_tokens_of_element:
				return cls.Kinds.Element, entry_begin, index

			if text[index] in ' \n\t':
				entry_begin = index + 1

			index += 1

		return cls.Kinds.End, index, -1

	@classmethod
	def _skip_other_block(cls, text: str, other_tokens: str, begin: int) -> int:
		"""対象外のブロックをスキップ

		Args:
			text (str): 解析対象の文字列
			other_tokens (str): 対象外の括弧のペア
			begin (int): 開始位置
		Returns:
			int: 読み取り終了位置
		"""
		index = begin
		other_closes: list[str] = []
		while index < len(text):
			if text[index] in other_tokens:
				other_index = other_tokens.find(text[index])
				if len(other_closes) > 0 and other_closes[-1] == other_tokens[other_index]:
					other_closes.pop()
				else:
					other_closes.append(other_tokens[other_index + 1])

			index += 1

			if len(other_closes) == 0:
				break

		return index

	@classmethod
	def _parse_block(cls, text: str, brackets: str, delimiter: str, begin: int, depth: int) -> tuple[int, list['BlockParser.Entry']]:
		"""ブロックを解析

		Args:
			text (str): 解析対象の文字列
			brackets (str): 括弧のペア
			delimiter (str): 区切り文字
			begin (int): 開始位置
			depth (int): 深度
		Returns:
			tuple[int, list[Entry]]: (読み取り終了位置, エントリーのリスト)
		"""
		index = begin
		entries: list[BlockParser.Entry] = []
		while index < len(text):
			if text[index] == brackets[1]:
				index += 1
				break

			in_progress, in_entries = cls._parse(text, brackets, delimiter, index, depth + 1)
			entries.extend(in_entries)
			index = in_progress

		return index, entries


def parse_bracket_block(text: str, brackets: str = '()') -> list[str]:
	"""文字列内の括弧で囲われた入れ子構造のブロックを展開する

	Args:
		text (str): 対象の文字列
		brackets (str): 括弧のペア (default: '()')
	Returns:
		list[str]: 展開したブロックのリスト
	"""
	root = BlockParser.parse(text, brackets, '')
	blocks = []
	for entry in [root, *root.unders()]:
		if entry.kind == BlockParser.Kinds.Block:
			blocks.append(text[entry.begin:entry.end])

	return blocks


def parse_pair_block(text: str, brackets: str = '{}', delimiter: str = ':') -> list[tuple[str, str]]:
	"""文字列内の連想配列の入れ子構造のブロックを展開する

	Args:
		text (str): 対象の文字列
		brackets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		list[tuple[str, str]]: [(キー, 値), ...]
	"""
	root = BlockParser.parse(text, brackets, delimiter)
	unders = sorted(root.unders(), key=lambda entry: entry.depth)
	pair_unders = [(unders[i * 2], unders[i * 2 + 1]) for i in range(int(len(unders) / 2)) if unders[i * 2].depth == unders[i * 2 + 1].depth]
	return [(text[key.begin:key.end], text[value.begin:value.end]) for key, value in pair_unders]


class Entry:
	"""ブロックエントリーの構成要素を管理"""

	type AltFormatter = Callable[[Entry], str | None]

	def __init__(self, before: str, brackets: str, delimiter: str) -> None:
		"""インスタンスを生成

		Args:
			before (str): 開始ブロックの前置詞
			brackets (str): 括弧のペア
			delimiter (str): 区切り文字
		"""
		self.before = before
		self.open = brackets[0]
		self.close = brackets[1]
		self.delimiter = delimiter
		self.elems: list[str | Entry] = []

	def __str__(self) -> str:
		"""str: 文字列表現"""
		return self.format()

	def __iter__(self) -> 'Iterator[str | Entry]':
		"""Iterator[str | Entry]: 要素のイテレーター"""
		for elem in self.flatten():
			yield elem

	@property
	def name(self) -> str:
		"""str: ブロックの名前。前置詞を左トリムした文字列"""
		return self.before.lstrip()

	def flatten(self) -> 'list[str | Entry]':
		"""全ての要素を平坦化して取得

		Returns:
			list[str | Entry]: 要素リスト
		"""
		elems: list[str | Entry] = []
		for elem in self.elems:
			if isinstance(elem, str):
				elems.append(elem)
			else:
				elems.extend(elem.flatten())

		return elems

	def format(self, join_format: str = '{delimiter} ', block_format: str = '{name}{open}{elems}{close}', alt_formatter: AltFormatter | None = None) -> str:
		"""指定した書式で文字列に変換

		Args:
			join_format (str): 要素の結合書式
			block_format (str): ブロックの書式
			alt_formatter (AltFormatter): 出力変換関数。文字列を返す場合にformatの結果を変更 (default = None)
		Returns:
			str: 変換後の文字列
		Note:
			### join_fomart
				* delimiter: 区切り文字
			### block_fomart
				* before: 開始ブロックの前置詞
				* name: ブロックの名前
				* open: 括弧(開)
				* close: 括弧(閉)
				* elems: 結合済みの要素
		"""
		if alt_formatter:
			alt_result = alt_formatter(self)
			if alt_result:
				return alt_result

		join_spliter = join_format.format(delimiter=self.delimiter)
		elems = join_spliter.join([elem.lstrip() if isinstance(elem, str) else elem.format(join_format, block_format, alt_formatter) for elem in self.elems])
		return block_format.format(before=self.before, name=self.name, open=self.open, close=self.close, elems=elems)


def parse_block_to_entry(text: str, brackets: str = '{}', delimiter: str = ':') -> Entry:
	"""文字列内の連想配列/関数コールの入れ子構造のブロックを展開する

	Args:
		text (str): 対象の文字列
		brackets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		Entry: 展開したブロックエントリー
	Raises:
		ValueError: 開閉ブロックが存在しない/対応関係が不正
	Note:
		展開したブロックに変換処理が必要な場合に有用
	"""
	def parse(entry: BlockParser.Entry) -> Entry:
		end = text.find(brackets[0], entry.begin)
		own = Entry(text[entry.begin:end], brackets, delimiter)
		for in_entry in entry.entries:
			if in_entry.kind == BlockParser.Kinds.Block:
				own.elems.append(parse(in_entry))
			else:
				own.elems.append(text[in_entry.begin:in_entry.end])

		return own

	root = BlockParser.parse(text, brackets, delimiter)
	return parse(root)
