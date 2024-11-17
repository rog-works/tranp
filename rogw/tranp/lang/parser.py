from collections.abc import Callable
from enum import Enum
import re
from typing import Iterator, TypeAlias


class Kinds(Enum):
	"""エントリーの種別"""
	Element = 'element'
	Block = 'block'
	End = 'end'


class Entry:
	"""エントリー(ブロック/要素)"""

	def __init__(self, begin: int, end: int, depth: int, kind: Kinds, entries: list['Entry']) -> None:
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

	def unders(self) -> Iterator['Entry']:
		"""配下の全エントリーを取得

		Args:
			Iterator[Entry]: エントリー
		"""
		for entry in self.entries:
			yield entry

			for in_entry in entry.entries:
				yield in_entry


AltFormatter: TypeAlias = Callable[['BlockFormatter'], str | None]


class BlockFormatter:
	"""ブロックフォーマッター"""

	def __init__(self, name: str, brackets: str, delimiter: str) -> None:
		"""インスタンスを生成

		Args:
			name (str): ブロックの名前
			brackets (str): 括弧のペア
			delimiter (str): 区切り文字
		"""
		self.name = name
		self.open = brackets[0]
		self.close = brackets[1]
		self.delimiter = delimiter
		self.elems: list[str | BlockFormatter] = []

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
				* name: ブロックの名前
				* open: 括弧(開)
				* close: 括弧(閉)
				* elems: 結合済みの要素
		"""
		if alt_formatter:
			alt_result = alt_formatter(self)
			if alt_result:
				return alt_result

		return self.block(join_format, block_format, alt_formatter)

	def block(self, join_format: str = '{delimiter} ', block_format: str = '{name}{open}{elems}{close}', alt_formatter: AltFormatter | None = None) -> str:
		"""指定した書式でブロックを生成

		Args:
			join_format (str): 要素の結合書式
			block_format (str): ブロックの書式
			alt_formatter (AltFormatter): 出力変換関数。文字列を返す場合にformatの結果を変更 (default = None)
		Returns:
			str: 変換後の文字列
		"""
		elems = [elem.lstrip() if isinstance(elem, str) else elem.format(join_format, block_format, alt_formatter) for elem in self.elems]
		join_spliter = join_format.format(delimiter=self.delimiter)
		join_elems = join_spliter.join(elems)
		return block_format.format(name=self.name, open=self.open, close=self.close, elems=join_elems)


class BlockParser:
	"""ブロックパーサー"""

	_all_pair = ['[]', '()', '{}', '<>', '""', "''"]

	@classmethod
	def parse(cls, text: str, brackets: str = '()', delimiter: str = ',') -> Entry:
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
	def _parse(cls, text: str, brackets: str, delimiter: str, begin: int, depth: int) -> tuple[int, list[Entry]]:
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
		entries: list[Entry] = []
		while index < len(text):
			kind, entry_begin, index_for_kind = cls._analyze_entry(text, brackets, delimiter, index)
			index = entry_begin
			if kind == Kinds.Block:
				end, in_entries = cls._parse_block(text, brackets, delimiter, index_for_kind + 1, depth)
				entries.append(Entry(index, end, depth, kind, in_entries))
				index = end + 1
			elif kind == Kinds.Element:
				entries.append(Entry(index, index_for_kind, depth, kind, []))
				index = index_for_kind
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
			return Kinds.Block, index, index
		elif text[index] == brackets[1]:
			return Kinds.End, index, -1

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
				return Kinds.Block, entry_begin, index
			elif text[index] in end_tokens_of_element:
				return Kinds.Element, entry_begin, index

			if text[index] in ' \n\t':
				entry_begin = index + 1

			index += 1

		return Kinds.End, index, -1

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
	def _parse_block(cls, text: str, brackets: str, delimiter: str, begin: int, depth: int) -> tuple[int, list[Entry]]:
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
		entries: list[Entry] = []
		while index < len(text):
			if text[index] == brackets[1]:
				index += 1
				break

			in_progress, in_entries = cls._parse(text, brackets, delimiter, index, depth + 1)
			entries.extend(in_entries)
			index = in_progress

		return index, entries

	@classmethod
	def parse_bracket(cls, text: str, brackets: str = '()') -> list[str]:
		"""文字列内の括弧で囲われた入れ子構造のブロックを展開する

		Args:
			text (str): 対象の文字列
			brackets (str): 括弧のペア (default: '()')
		Returns:
			list[str]: 展開したブロックのリスト
		"""
		root = cls.parse(text, brackets, '')
		blocks = []
		for entry in [root, *root.unders()]:
			if entry.kind == Kinds.Block:
				block_begin = text.find(brackets[0], entry.begin)
				blocks.append(text[block_begin:entry.end])

		return blocks

	@classmethod
	def parse_pair(cls, text: str, brackets: str = '{}', delimiter: str = ':') -> list[tuple[str, str]]:
		"""文字列内の連想配列の入れ子構造のブロックを展開する

		Args:
			text (str): 対象の文字列
			brackets (str): 括弧のペア (default: '{}')
			delimiter (str): 区切り文字 (default: ':')
		Returns:
			list[tuple[str, str]]: [(キー, 値), ...]
		"""
		root = cls.parse(text, brackets, delimiter)
		unders = sorted(root.unders(), key=lambda entry: entry.depth)
		pair_unders = [(unders[i * 2], unders[i * 2 + 1]) for i in range(int(len(unders) / 2)) if unders[i * 2].depth == unders[i * 2 + 1].depth]
		return [(text[key.begin:key.end], text[value.begin:value.end]) for key, value in pair_unders]

	@classmethod
	def parse_to_formatter(cls, text: str, brackets: str = '{}', delimiter: str = ':') -> BlockFormatter:
		"""文字列内の連想配列/関数コールの入れ子構造のブロックを展開し、フォーマッターを返却

		Args:
			text (str): 対象の文字列
			brackets (str): 括弧のペア (default: '{}')
			delimiter (str): 区切り文字 (default: ':')
		Returns:
			BlockFormatter: ブロックフォーマッター
		"""
		def to_formatter(entry: Entry) -> BlockFormatter:
			end = text.find(brackets[0], entry.begin)
			formatter = BlockFormatter(text[entry.begin:end], brackets, delimiter)
			for in_entry in entry.entries:
				if in_entry.kind == Kinds.Block:
					formatter.elems.append(to_formatter(in_entry))
				else:
					formatter.elems.append(text[in_entry.begin:in_entry.end])

			return formatter

		root = cls.parse(text, brackets, delimiter)
		return to_formatter(root)

	@classmethod
	def parse_primary(cls, text: str, brackets: str = '[]') -> list[str]:
		"""文字列内の第1層のブロックを解析し、左から順に展開する

		Args:
			text (str): 対象の文字列
			brackets (str): 括弧のペア (default: '{}')
		Returns:
			list[str]: ブロックリスト
		"""
		stack = 0
		blocks: list[str] = []
		index = 0
		begin = 0
		while index < len(text):
			if text[index] == brackets[0] and stack == 0:
				begin = index + 1
				stack += 1
			elif text[index] == brackets[0] and stack > 0:
				stack += 1
			elif text[index] == brackets[1] and stack == 1:
				blocks.append(text[begin:index])
				stack -= 1
			elif text[index] == brackets[1] and stack > 1:
				stack -= 1

			index += 1

		return blocks

	@classmethod	
	def break_separator(cls, text: str, delimiter: str) -> list[str]:
		"""文字列を区切り文字で分割

		Args:
			text (str): 対象の文字列
			delimiter (str): 区切り文字
		Returns:
			list[str]: ブロックリスト
		"""
		other_tokens = ''.join(cls._all_pair)
		blocks: list[str] = []
		index = 0
		begin = 0
		while index < len(text):
			if text[index] in other_tokens:
				index = cls._skip_other_block(text, other_tokens, index)
				continue

			if text[index] == delimiter:
				blocks.append(text[begin:index].strip(' '))
				begin = index + 1

			index += 1

		if begin < index:
			blocks.append(text[begin:index].strip(' '))

		return blocks


class DecoratorParser:
	"""デコレーターパーサー"""

	def __init__(self, decorator: str) -> None:
		"""インスタンスを生成

		Args:
			decorator (str): デコレーター
		"""
		self.decorator: str = decorator
		self._parsed: tuple[str, dict[str, str]] = ('', {})

	def _parse(self, decorator: str) -> tuple[str, dict[str, str]]:
		"""デコレーターを解析

		Args:
			decorator (str): デコレーター
		Returns:
			tuple[str, dict[str, str]]: (パス, 引数一覧)
		"""
		param_begin = decorator.find('(')
		join_params = decorator[param_begin + 1:len(decorator) - 1]
		params: dict[str, str] = {}
		for index, param_block in enumerate(BlockParser.break_separator(join_params, ',')):
			if param_block.count('=') > 0:
				label, *remain = param_block.split('=')
				params[label] = '='.join(remain)
			else:
				params[str(index)] = param_block

		param_begin = decorator.find('(')
		path = decorator[:param_begin]
		return path, params
	
	@property
	def path(self) -> str:
		"""str: デコレーターパス"""
		if len(self._parsed[0]) == 0:
			self._parsed = self._parse(self.decorator)

		return self._parsed[0]

	@property
	def args(self) -> dict[str, str]:
		"""dict[str, str]: 引数一覧"""
		if len(self._parsed[0]) == 0:
			self._parsed = self._parse(self.decorator)

		return self._parsed[1]

	@property
	def arg(self) -> str:
		"""str: 第1引数の値"""
		keys = list(self.args.keys())
		return self.args[keys[0]] if len(keys) > 0 else ''

	def any(self, *paths: str, **args: str) -> bool:
		"""指定のスキームと一致するか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			bool: True = 条件に合致
		"""
		if self.path not in paths:
			return False

		for label, subject in args.items():
			if label in self.args:
				if self.args[label] != subject:
					return False
			else:
				if subject not in self.args.values():
					return False

		return True

	def match(self, pattern: str) -> bool:
		"""指定のスキームと一致するか判定(正規表現)

		Args:
			pattern (str): 正規表現
		Returns:
			bool: True = 条件に合致
		"""
		return re.search(pattern, self.decorator) != None
