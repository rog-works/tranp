import re
from typing import NamedTuple


class Comment(NamedTuple):
	"""コメントデータ(クラス/関数共用)
	
	Attributes:
		description (str): 説明
		attributes (list[CommentAttribute]): メンバー変数リスト(クラス専用)
		args (list[CommentAttribute]): 引数リスト
		returns (list[CommentType]): 戻り値
		raises (list[CommentType]): 出力例外リスト
		note (str): 備考
		examples (str): サンプル
	"""

	class Attribute(NamedTuple):
		"""属性コメント

		Attributes:
			name (str): 名前
			type (str): 型
			description (str): 説明
		"""
		name: str
		type: str
		description: str

	class Type(NamedTuple):
		"""型コメント

		Attributes:
			type (str): 型
			description (str): 説明
		"""
		type: str
		description: str

	description: str
	attributes: list[Attribute]
	args: list[Attribute]
	returns: Type
	raises: list[Type]
	note: str
	examples: str

	@classmethod
	def parse(cls, text: str) -> 'Comment':
		"""コメントを解析してインスタンスを生成

		Args:
			text (str): コメントテキスト
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
		"""コメントを解析してメインの説明と各ブロックを分離

		Args:
			text (str): コメントテキスト
		Returns:
			tuple[str, dict[str, str]]: (メインの説明, ブロックリスト)
		"""
		tags = ['Attributes', 'Args', 'Returns', 'Raises', 'Note', 'Examples']
		joined_tags = '|'.join(tags)
		elems = cls.__each_trim(re.split(rf'(?:{joined_tags}):', text))
		seq_tags = re.findall(rf'({joined_tags}):', text)
		description, *block_contents = elems
		blocks = {tag: block_contents[index] for index, tag in enumerate(seq_tags)}
		return description, blocks

	@classmethod
	def parse_attributes(cls, block: str) -> list[Attribute]:
		"""属性ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			list[CommentAttribute]: 属性コメントリスト
		"""
		if len(block) == 0:
			return []

		attrs: list[Comment.Attribute] = []
		for line in block.split('\n'):
			matches = re.fullmatch(r'([^(]+)\(([^)+])\)\s*:\s*(.+)', line)
			if not matches:
				continue

			name, t, description = cls.__each_trim([matches[1], matches[2], matches[3]])
			attrs.append(Comment.Attribute(name, t, cls.__trim_description(description)))

		return attrs

	@classmethod
	def parse_returns(cls, block: str) -> Type:
		"""戻り値ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			CommentType: 型コメント
		"""
		matches = re.fullmatch(r'([^:]+):\s*(.+)', block)
		if not matches:
			return Comment.Type('', '')

		t, description = cls.__each_trim([matches[1], matches[2]])
		return Comment.Type(t, cls.__trim_description(description))

	@classmethod
	def parse_raises(cls, block: str) -> list[Type]:
		"""出力例外ブロックをパース

		Args:
			block (str): ブロックのテキスト
		Returns:
			list[CommentType]: 型コメントリスト
		"""
		if len(block) == 0:
			return []

		raises: list[Comment.Type] = []
		for line in block.split('\n'):
			matches = re.fullmatch(r'([^:]+):\s*(.+)', line)
			if not matches:
				continue

			t, description = cls.__each_trim([matches[1], matches[2]])
			raises.append(Comment.Type(t, cls.__trim_description(description)))

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
