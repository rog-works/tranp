import re
from typing import NamedTuple


class CommentAttribute(NamedTuple):
	"""コメント(属性)
	
	Attributes:
		name (str): 名前
		type (str): 型
		description (str): 説明
	"""

	name: str
	type: str
	description: str


class CommentType(NamedTuple):
	"""コメント(型)
	
	Attributes:
		type (str): 型
		description (str): 説明
	"""

	type: str
	description: str


class Comment(NamedTuple):
	"""コメント(クラス/関数共用)
	
	Attributes:
		description (str): 説明
		attributes (list[CommentAttribute]): メンバー変数リスト(クラス専用)
		args (list[CommentAttribute]): 引数リスト
		returns (list[CommentType]): 戻り値
		raises (list[CommentType]): 出力例外リスト
		note (str): 備考
		examples (str): サンプル
	"""

	description: str
	attributes: list[CommentAttribute]
	args: list[CommentAttribute]
	returns: CommentType
	raises: list[CommentType]
	note: str
	examples: str

	@classmethod
	def parse(cls, text: str) -> 'Comment':
		"""LONGSTRINGを解析してインスタンスを生成

		Args:
			text (str): LONGSTRING
		Returns:
			Comment: インスタンス
		"""
		description, blocks = cls.split_block(text)
		return cls(
			cls.__trim_description(description),
			cls.parse_attributes(blocks.get('Attributes', '')),
			cls.parse_attributes(blocks.get('Args', '')),
			cls.parse_returns(blocks.get('Returns', '')),
			cls.parse_raises(blocks.get('Raises', '')),
			cls.parse_note(blocks.get('Note', '')),
			cls.parse_examples(blocks.get('Examples', ''))
		)

	@classmethod
	def __trim_description(cls, text: str) -> str:
		"""説明用テキストの各行の前後の空白を除去

		Args:
			text (str): 説明用テキスト
		Returns:
			str: 処理後のテキスト
		"""
		return '\n'.join([elem.strip() for elem in text.split('\n')])

	@classmethod
	def __each_trim(cls, elems: list[str]) -> list[str]:
		"""要素テキストの前後の空白を除去

		Args:
			elems (list[str]): 要素テキストリスト
		Returns:
			list[str]: 処理後のテキストリスト
		"""
		return [elem.strip() for elem in elems]

	@classmethod
	def split_block(cls, text: str) -> tuple[str, dict[str, str]]:
		"""LONGSTRINGを解析してメインの説明と各ブロックを分離

		Args:
			text (str): LONGSTRING
		Returns:
			tuple[str, dict[str, str]]: (メインの説明, ブロックリスト)
		"""
		_text = text[4:-4]
		tags = ['Attributes', 'Args', 'Returns', 'Raises', 'Note', 'Examples']
		joined_tags = '|'.join(tags)
		elems = cls.__each_trim(re.split(rf'(?:{joined_tags}):', _text))
		seq_tags = re.findall(rf'({joined_tags}):', text)
		description, *block_contents = elems
		blocks = {tag: block_contents[index] for index, tag in enumerate(seq_tags)}
		return description, blocks

	@classmethod
	def parse_attributes(cls, block: str) -> list[CommentAttribute]:
		"""属性ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			list[CommentAttribute]: 属性コメントリスト
		"""
		if len(block) == 0:
			return []

		attrs: list[CommentAttribute] = []
		for line in block.split('\n'):
			left, description = cls.__each_trim(line.split(':'))
			name, wrap_t = cls.__each_trim(left.split(' '))
			t = wrap_t[1:-1]
			attrs.append(CommentAttribute(name, t, cls.__trim_description(description)))

		return attrs

	@classmethod
	def parse_returns(cls, block: str) -> CommentType:
		"""戻り値ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			CommentType: 型コメント
		"""
		if len(block) == 0:
			return CommentType('', '')

		t, description = cls.__each_trim(block.split(':'))
		return CommentType(t, cls.__trim_description(description))

	@classmethod
	def parse_raises(cls, block: str) -> list[CommentType]:
		"""出力例外ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			list[CommentType]: 型コメントリスト
		"""
		if len(block) == 0:
			return []

		raises: list[CommentType] = []
		for line in block.split('\n'):
			t, description = cls.__each_trim(line.split(':'))
			raises.append(CommentType(t, cls.__trim_description(description)))

		return raises

	@classmethod
	def parse_note(cls, block: str) -> str:
		"""備考ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			str: テキスト
		"""
		return cls.__trim_description(block)

	@classmethod
	def parse_examples(cls, block: str) -> str:
		"""サンプルブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			str: テキスト
		"""
		return cls.__trim_description(block)
