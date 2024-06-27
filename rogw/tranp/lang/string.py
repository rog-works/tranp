import re
from typing import Iterator, TypedDict


def camelize(org: str) -> str:
	"""アッパーキャメルケースに変換
	
	Args:
		org (str): 元の文字列
	Returns:
		str: 変換後の文字列
	"""
	return ''.join([elem.capitalize() for elem in org.split('_')])


def snakelize(org: str) -> str:
	"""スネークケースに変換
	
	Args:
		org (str): 元の文字列
	Returns:
		str: 変換後の文字列
	"""
	return re.sub('^[_]+', '', re.sub('([A-Z])', r'_\1', org).lower())


def parse_braket_block(text: str, brakets: str = '()') -> list[str]:
	"""文字列内の括弧で囲われたブロックを展開する

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '()')
	Returns:
		list[str]: 展開したブロックのリスト
	"""
	founds: list[tuple[int, int]] = []
	stack: list[int] = []
	index = 0
	while index < len(text):
		if text[index] in brakets:
			if text[index] == brakets[0]:
				stack.append(index)
			else:
				start = stack.pop()
				founds.append((start, index + 1))

		index = index + 1

	founds = sorted(founds, key=lambda entry: entry[0])
	return [text[found[0]:found[1]] for found in founds]


DictEntry = TypedDict('DictEntry', {'name': str, 'elems': list[str]})


def parse_block(text: str, brakets: str = '{}', delimiter: str = ':') -> list[DictEntry]:
	"""文字列内のブロックを展開する。対象: 連想配列, 関数コール

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		list[DictEntry]: [{'name': キー, 'elems': [値, ...]}, ...]
	"""
	chars = f'{brakets}{delimiter}'
	founds: list[tuple[int, str, list[str]]] = []
	stack: list[tuple[int, str, list[int]]] = []
	index = 0
	name = ''
	while index < len(text):
		if text[index] not in chars:
			# 空白以外を名前の構成要素とする
			if text[index] not in ' \n\t':
				name = name + text[index]
			else:
				name = ''

			index = index + 1
			continue

		if text[index] == brakets[0]:
			stack.append((index + 1, name, []))
			name = ''
		elif text[index] == delimiter:
			start, at_name, splits = stack.pop()
			splits.append(index)
			stack.append((start, at_name, splits))
		elif text[index] == brakets[1] and len(stack) > 0:
			start, at_name, splits = stack.pop()
			offsets = [*splits, index]
			curr = start
			in_texts: list[str] = []
			for offset in offsets:
				in_texts.append(text[curr:offset].lstrip())
				curr = offset + 1

			founds.append((start, at_name, in_texts))

		index = index + 1

	founds = sorted(founds, key=lambda entry: entry[0])
	return [{'name': found[1], 'elems': found[2]} for found in founds]


def parse_pair_block(text: str, brakets: str = '{}', delimiter: str = ':') -> list[tuple[str, str]]:
	"""文字列内のペアブロックを展開する。主に連想配列が対象

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		list[tuple[str, str]]: [(キー, 値), ...]
	"""
	return [(entry['elems'][0], entry['elems'][1]) for entry in parse_block(text, brakets, delimiter) if len(entry['elems']) == 2]


class Entry:
	"""ブロックエントリーの構成要素を管理"""

	def __init__(self, before: str, brakets: str, delimiter: str) -> None:
		"""インスタンスを生成

		Args:
			before (str): 開始ブロックの前置詞
			brakets (str): 括弧のペア
			delimiter (str): 区切り文字
		"""
		self.before = before
		self.open = brakets[0]
		self.close = brakets[1]
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

	def format(self, join_format: str = '{delimiter} ', block_format: str = '{name}{open}{elems}{close}') -> str:
		"""文字列表現 (書式指定版)

		Args:
			join_format (str): 要素の結合書式
			block_format (str): ブロックの書式
		Returns:
			str: 文字列表現
		Note:
			* join_fomart
				* delimiter: 区切り文字
			* block_fomart
				* before: 開始ブロックの前置詞
				* name: ブロックの名前
				* open: 括弧(開)
				* close: 括弧(閉)
				* elems: 結合済みの要素
		"""
		join_spliter = join_format.format(delimiter=self.delimiter)
		elems = join_spliter.join([elem.lstrip() if isinstance(elem, str) else elem.format(join_format, block_format) for elem in self.elems])
		return block_format.format(before=self.before, name=self.name, open=self.open, close=self.close, elems=elems)


def parse_nested_block(text: str, brakets: str = '{}', delimiter: str = ':') -> Entry:
	"""文字列内の入れ子構造のブロックを展開する。対象: 連想配列, 関数コール

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		Entry: 展開したブロックエントリー
	"""
	braket_o = brakets[0]
	braket_c = brakets[1]
	braket_o_escaped = re.sub(r'([\[\(])', r'\\\1', braket_o)
	braket_c_escaped = re.sub(r'([\]\)])', r'\\\1', braket_c)
	brakets_escaped = f'{braket_o_escaped}{braket_c_escaped}'
	matcher_begin = re.compile(rf'[^{braket_o_escaped}]*{braket_o_escaped}')
	matcher_elem = re.compile(rf'[^{brakets_escaped}{delimiter}]*[{brakets_escaped}{delimiter}]')

	def parse(in_text: str) -> tuple[int, Entry]:
		begin = matcher_begin.match(in_text)
		if begin is None:
			raise ValueError('Not found open braket. text: {text}')

		entry = Entry(begin[0][:-1], brakets, delimiter)
		remain = in_text[len(begin[0]):]
		offset = 0
		while len(remain) > 0:
			matches = matcher_elem.match(remain)
			if matches is None:
				offset = len(remain)
				break

			progress = len(matches[0])
			elem, tail = matches[0][:-1], matches[0][-1]
			if tail == braket_c:
				if len(elem) > 0:
					entry.elems.append(elem)

				offset += progress
				break

			if tail == braket_o:
				in_progress, in_entry = parse(remain)
				entry.elems.append(in_entry)
				offset += in_progress
				remain = remain[in_progress:]
			elif tail == delimiter:
				entry.elems.append(elem)
				offset += progress
				remain = remain[progress:]

		return len(begin[0]) + offset, entry

	return parse(text)[1]
