from collections.abc import Callable
from typing import ClassVar, TypeAlias

from rogw.tranp.compatible.cpp.classes import char, void
from rogw.tranp.compatible.cpp.enum import CEnum as Enum
from rogw.tranp.compatible.cpp.object import CP, CSP
from rogw.tranp.compatible.python.embed import Embed

from example.FW.string import String


class JsonEntryTypes(Enum):
	"""JSONエントリーの種別"""
	Unknown = 0
	Boolean = 1
	Number = 2
	String = 3
	Array = 4
	Object = 5


JsonEntryInfo: TypeAlias = tuple[str, int, int]


class JsonParser:
	"""JSONパーサー"""

	@classmethod
	def parse(cls, json_str: str) -> list[JsonEntryInfo]:
		"""JSON文字列を解析

		Args:
			json_str (str): JSON文字列
		Returns:
			list[JsonEntryInfo]: JSONエントリー情報リスト
		"""
		return cls._parse_entry(json_str, 0, '')[0]

	@classmethod
	def _parse_entry(cls, json_str: str, begin: int, path: str) -> tuple[list[JsonEntryInfo], int]:
		"""JSON文字列を解析(エントリー)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
			path (str): エントリーパス
		Returns:
			tuple[list[JsonEntryInfo], int]: JSONエントリー情報リスト, 読み取り終了位置
		"""
		end = begin
		info_list: list[JsonEntryInfo] = []
		at_type, begin_value = cls._analyze_type(json_str, begin)
		end = begin_value
		if at_type == JsonEntryTypes.Boolean:
			end = cls._parse_boolean(json_str, begin_value)
			info_list.append((path, begin_value, end))
		elif at_type == JsonEntryTypes.Number:
			end = cls._parse_number(json_str, begin_value)
			info_list.append((path, begin_value, end))
		elif at_type == JsonEntryTypes.String:
			end = cls._parse_string(json_str, begin_value)
			info_list.append((path, begin_value, end))
		elif at_type == JsonEntryTypes.Array:
			in_entries, next_pos = cls._parse_array(json_str, begin_value, path)
			end = next_pos
			info_list.append((path, begin_value, end))
			info_list.extend(in_entries)
		elif at_type == JsonEntryTypes.Object:
			in_entries, next_pos = cls._parse_object(json_str, begin_value, path)
			end = next_pos
			info_list.append((path, begin_value, end))
			info_list.extend(in_entries)

		return (info_list, end)

	@classmethod
	def _parse_boolean(cls, json_str: str, begin: int) -> int:
		"""JSON文字列を解析(エントリー/Boolean)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
		Returns:
			int: 読み取り終了位置
		"""
		end = begin
		string = ''
		while end < len(json_str):
			string += json_str[end]
			if string == 'false' or string == 'true':
				break

			end += 1

		return end + 1

	@classmethod
	def _parse_number(cls, json_str: str, begin: int) -> int:
		"""JSON文字列を解析(エントリー/Number)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
		Returns:
			int: 読み取り終了位置
		"""
		end = begin
		while end < len(json_str):
			end += 1
			if not String.is_number(json_str, begin, end + 1):
				break

		return end

	@classmethod
	def _parse_string(cls, json_str: str, begin: int) -> int:
		"""JSON文字列を解析(エントリー/String)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
		Returns:
			int: 読み取り終了位置
		"""
		end = json_str.find('\"', begin)
		while end < len(json_str):
			end += 1
			if json_str[end - 1] == char('\\') and json_str[end] == char('"'):
				continue

			if json_str[end] == char('"'):
				break

		return end + 1

	@classmethod
	def _parse_array(cls, json_str: str, begin: int, path: str) -> tuple[list[JsonEntryInfo], int]:
		"""JSON文字列を解析(エントリー/Array)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
			path (str): エントリーパス
		Returns:
			tuple[list[JsonEntryInfo], int]: JSONエントリー情報リスト, 読み取り終了位置
		"""
		end = json_str.find('[', begin)
		info_list: list[JsonEntryInfo] = []
		end += 1
		element_at = 0
		while end < len(json_str):
			entry_type = cls._analyze_type(json_str, end, ']')[0]
			if entry_type == JsonEntryTypes.Unknown or json_str[end] == char(']'):
				break

			in_info_list, next_pos = cls._parse_entry(json_str, end, cls.join_path(path, str(element_at)))
			end = next_pos
			info_list.extend(in_info_list)
			element_at += 1

		return (info_list, end + 1)

	@classmethod
	def _parse_object(cls, json_str: str, begin: int, path: str) -> tuple[list[JsonEntryInfo], int]:
		"""JSON文字列を解析(エントリー/Object)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
			path (str): エントリーパス
		Returns:
			tuple[list[JsonEntryInfo], int]: JSONエントリー情報リスト, 読み取り終了位置
		"""
		end = json_str.find('{', begin)
		info_list: list[JsonEntryInfo] = []
		end += 1
		while end < len(json_str):
			entry_type = cls._analyze_type(json_str, end, '}')[0]
			if entry_type == JsonEntryTypes.Unknown or json_str[end] == char('}'):
				break

			key, begin_value = cls._parse_key(json_str, end)
			in_info_list, next_pos = cls._parse_entry(json_str, begin_value, cls.join_path(path, key))
			end = next_pos
			info_list.extend(in_info_list)

		return (info_list, end + 1)

	@classmethod
	def _parse_key(cls, json_str: str, begin: int) -> tuple[str, int]:
		"""JSON文字列を解析(キー)

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
		Returns:
			tuple[str, int]: キー, 読み取り終了位置
		"""
		key_begin = json_str.find('\"', begin)
		end = json_str.find('\"', key_begin + 1)
		key = json_str[key_begin + 1:end]
		return (key, end + 1)

	@classmethod
	def analyze_type(cls, json_str: str, begin: int) -> JsonEntryTypes:
		"""JSONエントリーの種別を解析

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
		Returns:
			JsonEntryTypes: JSONエントリーの種別
		Raises:
			RuntimeError: 解析に失敗
		"""
		entry_type = cls._analyze_type(json_str, begin)[0]
		if entry_type == JsonEntryTypes.Unknown:
			raise RuntimeError('Invalid JSON schema. json_str: {json}, begin: {begin}'.format(json=json_str, begin=begin))

		return entry_type

	@classmethod
	def _analyze_type(cls, json_str: str, begin: int, end_token: str = '') -> tuple[JsonEntryTypes, int]:
		"""JSONエントリーの種別を解析

		Args:
			json_str (str): JSON文字列
			begin (int): 読み取り開始位置
			end_token (str): 終端記号 (default = '')
		Returns:
			tuple[JsonEntryTypes, int]: JSONエントリーの種別, 読み取り終了位置
		"""
		end = begin
		while end < len(json_str):
			if json_str[end] == char('f') or json_str[end] == char('t'):
				return (JsonEntryTypes.Boolean, end)
			elif json_str[end] == char('"'):
				return (JsonEntryTypes.String, end)
			elif json_str[end] == char('['):
				return (JsonEntryTypes.Array, end)
			elif json_str[end] == char('{'):
				return (JsonEntryTypes.Object, end)
			elif String.is_number(json_str, end, end + 1):
				return (JsonEntryTypes.Number, end)
			elif len(end_token) > 0 and json_str[end] == end_token[0]:
				return (JsonEntryTypes.Unknown, -1)

			end += 1

		return (JsonEntryTypes.Unknown, -1)

	@classmethod
	def join_path(cls, path0: str, path1: str) -> str:
		"""パスを連結

		Args:
			path1 (str): パス0
			path2 (str): パス1
		Returns:
			str: 連結したパス
		"""
		return path0 + '.' + path1 if len(path0) > 0 else path1


@Embed.struct
class JsonEntity:
	"""JSONエントリーの実体を管理"""

	as_bool: bool
	as_number: float
	as_string: str

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.as_bool: bool = False
		self.as_number: float = 0
		self.as_string: str = ''

	@classmethod
	def for_scalar(cls, value_str: str, entry_type: JsonEntryTypes) -> 'JsonEntity':
		"""スカラー型用にインスタンスを生成

		Args:
			value_str (str): 文字列
			entry_type (JsonEntryTypes): JSONエントリーの種別
		Returns:
			JsonEntity: インスタンス
		"""
		instance = cls()
		if entry_type == JsonEntryTypes.Boolean:
			instance.as_bool = value_str == 'true'
		elif entry_type == JsonEntryTypes.Number:
			instance.as_number = float(value_str)
		elif entry_type == JsonEntryTypes.String:
			instance.as_string = String.unescape(value_str[1:len(value_str) - 1])

		return instance


@Embed.struct
class JsonEntry:
	"""JSONエントリー"""

	path: str
	entry_type: JsonEntryTypes
	entity: JsonEntity

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.path: str = ''
		self.entry_type: JsonEntryTypes = JsonEntryTypes.Unknown
		self.entity: JsonEntity

	@classmethod
	def make(cls, path: str, entry_type: JsonEntryTypes, entity: JsonEntity) -> 'JsonEntry':
		"""インスタンスを生成

		Args:
			path (str): JSONパス
			entry_type (JsonEntryTypes): JSONエントリーの種別
			entity (JsonEntity): JSONエンティティー
		Returns:
			JsonEntry: インスタンス
		"""
		instance = cls()
		instance.path = path
		instance.entry_type = entry_type
		instance.entity = entity
		return instance


class Json:
	"""JSON"""

	_to_type_names: ClassVar[dict[JsonEntryTypes, str]] = {
		JsonEntryTypes.Boolean: bool.__name__,
		JsonEntryTypes.Number: float.__name__,
		JsonEntryTypes.String: str.__name__,
		JsonEntryTypes.Array: list.__name__,
		JsonEntryTypes.Object: 'Json',
	}

	_jsons: 'list[CSP[Json]]'
	_entries: list[JsonEntry]
	_root: 'CP[Json]'
	_entry_id: int

	def __init__(self) -> None:
		"""インスタンスを生成"""
		super().__init__()
		self._jsons: list[CSP[Json]] = []
		self._entries: list[JsonEntry] = []
		self._root: CP[Json] = CP(self)
		self._entry_id: int = 0

	@Embed.python
	def __repr__(self) -> str:
		"""Returns: str: シリアライズ表現"""
		return '<{cls}[{type}]: \"{path}\" at {addr}>'.format(cls=Json.__name__, type=self.entry_type.name, path=self.path, addr=hex(id(self)))

	@classmethod
	def instantiate(cls) -> 'CSP[Json]':
		"""オブジェクト型の空のインスタンスを生成

		Returns:
			CSP[Json]: インスタンス
		"""
		return cls.parse('{}')

	@classmethod
	def parse(cls, json_str: str) -> 'CSP[Json]':
		"""JSON文字列を基にインスタンスを生成

		Args:
			json_str (str): JSON文字列
		Returns:
			CSP[Json]: インスタンス
		"""
		root = CSP.new(Json())
		info_list = JsonParser.parse(json_str)
		for entry_id in range(len(info_list)):
			path, begin, end = info_list[entry_id]
			entry_type = JsonParser.analyze_type(json_str, begin)
			if entry_type == JsonEntryTypes.Boolean or entry_type == JsonEntryTypes.Number or entry_type == JsonEntryTypes.String:
				root.on._jsons.append(root.on._make_for_entry(entry_id))
				root.on._entries.append(JsonEntry.make(path, entry_type, JsonEntity.for_scalar(json_str[begin:end], entry_type)))
			else:
				root.on._jsons.append(root.on._make_for_entry(entry_id))
				root.on._entries.append(JsonEntry.make(path, entry_type, JsonEntity()))

		return root

	def _jsonify_of_bool(self, value: bool) -> 'CSP[Json]':
		"""スカラー値からJSONインスタンスに変換(Boolean)

		Args:
			value (bool): 値
		Returns:
			CSP[Json]: インスタンス
		"""
		return Json.parse('true' if value else 'false')

	def _jsonify_of_number(self, value: float) -> 'CSP[Json]':
		"""スカラー値からJSONインスタンスに変換(Number)

		Args:
			value (bool): 値
		Returns:
			CSP[Json]: インスタンス
		"""
		return Json.parse(str(value))

	def _jsonify_of_string(self, value: str) -> 'CSP[Json]':
		"""スカラー値からJSONインスタンスに変換(String)

		Args:
			value (bool): 値
		Returns:
			CSP[Json]: インスタンス
		"""
		return Json.parse('\"' + String.escape(value, char('"')) + '\"')

	def _make_for_entry(self, entry_id: int) -> 'CSP[Json]':
		"""エントリー用にインスタンスを生成

		Args:
			entry_id (int): エントリーID
		Returns:
			CSP[Json]: インスタンス
		"""
		under = CSP.new(Json())
		under.on._root = CP(self)
		under.on._entry_id = entry_id
		return under

	def _is_under(self, path: str) -> bool:
		"""自身の配下要素のパスか判定

		Args:
			path (str): パス
		Returns:
			bool: True = 配下要素
		"""
		if not (len(self.path) < len(path)):
			return False

		if not self._starts_with(path, self.path):
			return False

		dots1 = path.count('.')
		if len(self.path) == 0:
			return dots1 == 0

		dots0 = self.path.count('.')
		return dots0 + 1 == dots1

	def scalar_with(self, expected_type: JsonEntryTypes = JsonEntryTypes.Unknown) -> bool:
		"""指定のスカラー型か判定。引数を省略した場合は、スカラー型か否かを判定

		Args:
			expected_type (JsonEntryTypes): 判定するJSONエントリーの種別 (default = NotFound)
		Returns:
			bool: True = スカラー型, False = Array/Object
		"""
		if expected_type == JsonEntryTypes.Unknown:
			return self.entry_type == JsonEntryTypes.Boolean or self.entry_type == JsonEntryTypes.Number or self.entry_type == JsonEntryTypes.String

		return self.entry_type == expected_type

	def _at_json(self, entry_id: int) -> 'CP[Json]':
		"""指定エントリーのJSONを取得

		Args:
			entry_id (int): エントリーID
		Returns:
			CP[Json]: JSON
		"""
		return self.root.on._jsons[entry_id].addr

	@property
	def is_root(self) -> bool:
		"""Returns: bool: True = ルートオブジェクト"""
		return self._root is None

	@property
	def root(self) -> 'CP[Json]':
		"""Returns: CP[Json]: ルートオブジェクト"""
		return self._root if self._root else CP(self)

	@property
	def path(self) -> str:
		"""Returns: str: JSONパス"""
		return self.root.on._entries[self._entry_id].path

	@property
	def symbol(self) -> str:
		"""Returns: str: シンボル名"""
		index = self.path.rfind('.')
		return self.path[index + 1:] if index != -1 else self.path

	@property
	def entry_type(self) -> JsonEntryTypes:
		"""Returns: JsonEntryTypes: JSONエントリーの種別"""
		return self.root.on._entries[self._entry_id].entry_type

	@property
	def type_name(self) -> str:
		"""Returns: str: 型の名前"""
		return Json._to_type_names[self.entry_type]

	@property
	def entity_at(self) -> CP[void]:
		"""Returns: CP[void]: 実体のアドレス"""
		if self.scalar_with(JsonEntryTypes.Boolean):
			return CP(self.root.on._entries[self._entry_id].entity.as_bool)
		elif self.scalar_with(JsonEntryTypes.Number):
			return CP(self.root.on._entries[self._entry_id].entity.as_number)
		elif self.scalar_with(JsonEntryTypes.String):
			return CP(self.root.on._entries[self._entry_id].entity.as_string)
		else:
			return self._at_json(self._entry_id)

	def exists(self, jsonpath: str) -> bool:
		"""指定のJSONパスを持つ要素が存在するか判定

		Args:
			jsonpath (str): JSONパス
		Returns:
			bool: True = 存在
		"""
		for entry in self.root.on._entries:
			if jsonpath == entry.path:
				return True

		return False

	def has_key(self, key: str) -> bool:
		"""指定のキーを持つ配下要素が存在するか判定

		Args:
			key (str): キー
		Returns:
			bool: True = 存在
		"""
		return self.exists(JsonParser.join_path(self.path, key))

	def unders(self) -> 'list[CP[Json]]':
		"""配下要素を取得

		Returns:
			list[CP[Json]]: 配下要素のリスト
		"""
		under_values: list[CP[Json]] = []
		remain = len(self.root.on._entries) - self._entry_id
		for i in range(remain):
			entry_id = i + self._entry_id
			entry_json = self._at_json(entry_id)
			if self._is_under(entry_json.on.path):
				under_values.append(entry_json)

		return under_values

	def at(self, index: int) -> 'CP[Json]':
		"""配下要素を取得

		Args:
			index (int): インデックス
		Returns:
			CP[Json]: インスタンス
		Raises:
			RuntimeError: 存在しないエントリーを指定
		"""
		return self.fetch(JsonParser.join_path(self.path, str(index)))

	def by(self, key: str) -> 'CP[Json]':
		"""配下要素を取得

		Args:
			key (str): シンボル名
		Returns:
			CP[Json]: インスタンス
		Raises:
			RuntimeError: 存在しないエントリーを指定
		"""
		return self.fetch(JsonParser.join_path(self.path, key))

	def fetch(self, jsonpath: str) -> 'CP[Json]':
		"""JSONパスと一致するエントリーを取得

		Args:
			jsonpath (str): JSONパス
		Returns:
			CP[Json]: インスタンス
		Raises:
			RuntimeError: 存在しないエントリーを指定
		"""
		for entry_id in range(len(self.root.on._entries)):
			entry_json = self._at_json(entry_id)
			if jsonpath == entry_json.on.path:
				return entry_json

		raise RuntimeError('Entry not found. jsonpath: {path}'.format(path=jsonpath))

	def filter(self, query: 'Callable[[CP[Json]], bool]') -> 'list[CP[Json]]':
		"""フィルター条件に一致する要素を取得

		Args:
			query (Callable[[CP[Json]], bool]): フィルター関数
		Returns:
			list[CP[Json]]: 要素リスト
		"""
		return [in_json.addr for in_json in self._jsons if query(in_json.addr)]

	def diff(self, other: 'CP[Json]') -> 'list[str]':
		"""相違個所のパスを抽出

		Args:
			other (CP[Json]): 比較対象
		Returns:
			list[str]: パスリスト
		Note:
			パスには自身と比較対象、双方のパスが混在する点に注意
		"""
		diff_paths: list[str] = []
		if self.entry_type != other.on.entry_type:
			diff_paths.append(self.path)
		elif self.scalar_with(JsonEntryTypes.Boolean) and self.as_bool != other.on.as_bool:
			diff_paths.append(self.path)
		elif self.scalar_with(JsonEntryTypes.Number) and self.as_number != other.on.as_number:
			diff_paths.append(self.path)
		elif self.scalar_with(JsonEntryTypes.String) and self.as_string != other.on.as_string:
			diff_paths.append(self.path)
		elif not self.scalar_with():
			for under in self.unders():
				if other.on.has_key(under.on.symbol):
					diff_paths.extend(under.on.diff(other.on.by(under.on.symbol)))
				else:
					diff_paths.append(under.on.path)

			for under in other.on.unders():
				if not self.has_key(under.on.symbol):
					diff_paths.append(under.on.path)

			if len(diff_paths) > 0:
				diff_paths.append(self.path)

		return diff_paths

	@property
	def as_bool(self) -> bool:
		"""Returns: bool: 値 Raises: RuntimeError: Boolean以外で使用"""
		if not self.scalar_with(JsonEntryTypes.Boolean):
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		return self.root.on._entries[self._entry_id].entity.as_bool

	@property
	def as_number(self) -> float:
		"""Returns: float: 値 Raises: RuntimeError: Number以外で使用"""
		if not self.scalar_with(JsonEntryTypes.Number):
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		return self.root.on._entries[self._entry_id].entity.as_number

	@property
	def as_string(self) -> str:
		"""Returns: str: 値 Raises: RuntimeError: String以外で使用"""
		if not self.scalar_with(JsonEntryTypes.String):
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		return self.root.on._entries[self._entry_id].entity.as_string

	def set_bool(self, value: bool) -> None:
		"""値を更新(Boolean)

		Args:
			value (str): 値
		"""
		if self.scalar_with():
			self.root.on._entries[self._entry_id].entity.as_bool = value
			self.root.on._entries[self._entry_id].entry_type = JsonEntryTypes.Boolean
		else:
			self._swap_entry(self._jsonify_of_bool(value))

	def set_number(self, value: float) -> None:
		"""値を更新(Number)

		Args:
			value (str): 値
		"""
		if self.scalar_with():
			self.root.on._entries[self._entry_id].entity.as_number = value
			self.root.on._entries[self._entry_id].entry_type = JsonEntryTypes.Number
		else:
			self._swap_entry(self._jsonify_of_number(value))

	def set_string(self, value: str) -> None:
		"""値を更新(String)

		Args:
			value (str): 値
		"""
		if self.scalar_with():
			self.root.on._entries[self._entry_id].entity.as_string = value
			self.root.on._entries[self._entry_id].entry_type = JsonEntryTypes.String
		else:
			self._swap_entry(self._jsonify_of_string(value))

	def set_array(self, value: 'CP[Json]') -> None:
		"""値を更新(Array)

		Args:
			value (CP[Json]): 値
		Raises:
			RuntimeError: Array以外を指定
		"""
		if value.on.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Type not match. type_name: {type}'.format(type=value.on.type_name))

		self._swap_entry(value.on.isolate())

	def set_object(self, value: 'CP[Json]') -> None:
		"""値を更新(Object)

		Args:
			value (CP[Json]): 値
		Raises:
			RuntimeError: Object以外を指定
		"""
		if value.on.entry_type != JsonEntryTypes.Object:
			raise RuntimeError('Type not match. type_name: {type}'.format(type=value.on.type_name))

		self._swap_entry(value.on.isolate())

	def set_json(self, value: 'CP[Json]') -> None:
		"""値を更新(汎用)

		Args:
			value (CP[Json]): 値
		"""
		if value.on.scalar_with(JsonEntryTypes.Boolean):
			self.set_bool(value.on.as_bool)
		elif value.on.scalar_with(JsonEntryTypes.Number):
			self.set_number(value.on.as_number)
		elif value.on.scalar_with(JsonEntryTypes.String):
			self.set_string(value.on.as_string)
		elif value.on.scalar_with(JsonEntryTypes.Array):
			self.set_array(value)
		else:
			self.set_object(value)

	def apply_bool_to(self, key: str, value: bool) -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(Boolean)

		Args:
			key (str): キー
			value (bool): 値
		"""
		jsonpath = JsonParser.join_path(self.path, key)
		if self.exists(jsonpath):
			self.fetch(jsonpath).on.set_bool(value)
		else:
			self._add_entry(key, self._jsonify_of_bool(value))

	def apply_number_to(self, key: str, value: float) -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(Number)

		Args:
			key (str): キー
			value (float): 値
		"""
		jsonpath = JsonParser.join_path(self.path, key)
		if self.exists(jsonpath):
			self.fetch(jsonpath).on.set_number(value)
		else:
			self._add_entry(key, self._jsonify_of_number(value))

	def apply_string_to(self, key: str, value: str) -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(String)

		Args:
			key (str): キー
			value (str): 値
		"""
		jsonpath = JsonParser.join_path(self.path, key)
		if self.exists(jsonpath):
			self.fetch(jsonpath).on.set_string(value)
		else:
			self._add_entry(key, self._jsonify_of_string(value))

	def apply_array_to(self, key: str, value: 'CP[Json]') -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(Array)

		Args:
			key (str): キー
			value (CP[Json]): 値
		Raises:
			RuntimeError: Array以外を指定
		"""
		if value.on.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Type not match. type_name: {type}'.format(type=value.on.type_name))

		jsonpath = JsonParser.join_path(self.path, key)
		if self.exists(jsonpath):
			self.fetch(jsonpath).on.set_array(value)
		else:
			self._add_entry(key, value.on.isolate())

	def apply_object_to(self, key: str, value: 'CP[Json]') -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(Object)

		Args:
			key (str): キー
			value (CP[Json]): 値
		Raises:
			RuntimeError: Object以外を指定
		"""
		if value.on.entry_type != JsonEntryTypes.Object:
			raise RuntimeError('Type not match. type_name: {type}'.format(type=value.on.type_name))

		jsonpath = JsonParser.join_path(self.path, key)
		if self.exists(jsonpath):
			self.fetch(jsonpath).on.set_object(value)
		else:
			self._add_entry(key, value.on.isolate())

	def apply_json_to(self, key: str, value: 'CP[Json]') -> None:
		"""指定のキーの要素に値を反映。存在しない場合は要素を追加(汎用)

		Args:
			key (str): キー
			value (CP[Json]): 値
		"""
		if value.on.scalar_with(JsonEntryTypes.Boolean):
			self.apply_bool_to(key, value.on.as_bool)
		elif value.on.scalar_with(JsonEntryTypes.Number):
			self.apply_number_to(key, value.on.as_number)
		elif value.on.scalar_with(JsonEntryTypes.String):
			self.apply_string_to(key, value.on.as_string)
		elif value.on.entry_type == JsonEntryTypes.Array:
			self.apply_array_to(key, value)
		else:
			self.apply_object_to(key, value)

	def apply_bool_at(self, index: int, value: bool) -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Boolean)

		Args:
			index (int): インデックス
			value (bool): 値
		Raises:
			RuntimeError: Array以外で使用
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.apply_bool_to(str(index), value)

	def apply_number_at(self, index: int, value: float) -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Number)

		Args:
			index (int): インデックス
			value (float): 値
		Raises:
			RuntimeError: Array以外で使用
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.apply_number_to(str(index), value)

	def apply_string_at(self, index: int, value: str) -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(String)

		Args:
			index (int): インデックス
			value (str): 値
		Raises:
			RuntimeError: Array以外で使用
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.apply_string_to(str(index), value)

	def apply_array_at(self, index: int, value: 'CP[Json]') -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Array)

		Args:
			index (int): インデックス
			value (CP[Json]): 値
		Raises:
			RuntimeError: Array以外で使用
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.apply_array_to(str(index), value)

	def apply_object_at(self, index: int, value: 'CP[Json]') -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(Object)

		Args:
			index (int): インデックス
			value (CP[Json]): 値
		Raises:
			RuntimeError: Array以外で使用
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.apply_object_to(str(index), value)

	def apply_json_at(self, index: int, value: 'CP[Json]') -> None:
		"""指定のインデックスの要素に値を反映。存在しない場合は要素を追加(汎用)

		Args:
			index (int): インデックス
			value (CP[Json]): 値
		"""
		self.apply_json_to(str(index), value)

	def remove_at(self, index: int) -> None:
		"""指定のインデックスの要素を削除

		Args:
			index (int): インデックス
		Raises:
			RuntimeError: Array以外で使用
			RuntimeError: 存在しないエントリーを指定
		"""
		if self.entry_type != JsonEntryTypes.Array:
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self.remove_by(str(index))

	def remove_by(self, key: str) -> None:
		"""指定のキーの要素を削除

		Args:
			key (str): キー
		Raises:
			RuntimeError: Array/Object以外で使用
			RuntimeError: 存在しないエントリーを指定
		"""
		if self.scalar_with():
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		jsonpath = JsonParser.join_path(self.path, key)
		if not self.exists(jsonpath):
			raise RuntimeError('Entry not found. jsonpath: {path}'.format(path=jsonpath))

		self._remove_entry(self.fetch(jsonpath).on._entry_id)

	def _add_entry(self, key: str, entry_json: 'CSP[Json]') -> None:
		"""自身の配下にJSONエントリーを追加

		Args:
			key (str): キー
			entry_json (CSP[Json]): JSON
		Raises:
			RuntimeError: Array/Object以外で使用
		Note:
			XXX このメソッドを実行する前に必ずexists/has_keyで重複がないことを確認すること
		"""
		if self.scalar_with():
			raise RuntimeError('Operation not allowed. type_name: {type}'.format(type=self.type_name))

		self._insert_entry(len(self.root.on._entries), JsonParser.join_path(self.path, key), entry_json)

	def _swap_entry(self, entry_json: 'CSP[Json]') -> None:
		"""自身のエントリーを基点に新たなJSONエントリーに置き換え

		Args:
			entry_json (CSP[Json]): JSON
		"""
		self_path = self.path
		self._remove_entry(self._entry_id)
		self._insert_entry(self._entry_id, self_path, entry_json)

	def _remove_entry(self, entry_id: int) -> None:
		"""指定位置のJSONエントリーとその下位要素を削除

		Args:
			entry_id (int): エントリーID
		"""
		relayed_ids = self._relayed_entry_ids(entry_id)
		for i in range(len(relayed_ids)):
			index = len(relayed_ids) - 1 - i
			relayed_id = entry_id + index
			del self.root.on._jsons[relayed_id]
			del self.root.on._entries[relayed_id]

	def _insert_entry(self, begin_id: int, begin_path: str, entry_json: 'CSP[Json]') -> None:
		"""指定位置にJSONエントリーを挿入

		Args:
			begin_id (int): 挿入開始位置
			begin_path (str): 基準のJSONパス
			entry_json (CSP[Json]): JSON
		"""
		# ルートではない場合、ルートオブジェクトに変換
		if not entry_json.on.is_root:
			entry_json = entry_json.on.isolate()

		# JSONエントリーを挿入
		for i in range(len(entry_json.on.root.on._entries)):
			org_entry = entry_json.on.root.on._entries[i]
			new_path = JsonParser.join_path(begin_path, org_entry.path) if i > 0 else begin_path
			new_entry_id = begin_id + i
			self.root.on._jsons.insert(new_entry_id, self.root.on._make_for_entry(new_entry_id))
			self.root.on._entries.insert(new_entry_id, JsonEntry.make(new_path, org_entry.entry_type, org_entry.entity))

		# 挿入位置の末尾から先の既存要素のエントリーIDを修正
		post_id = begin_id + len(entry_json.on.root.on._entries)
		remain = len(self.root.on._entries) - post_id
		for i in range(remain):
			new_entry_id = post_id + i
			in_entry_json = self._at_json(new_entry_id)
			in_entry_json.on._entry_id = new_entry_id

	def isolate(self) -> 'CSP[Json]':
		"""自身を基点に新たなインスタンスを生成

		Returns:
			CSP[Json]: インスタンス
		Note:
			* ルート要素との参照を切り離すことでメモリー安全な複製として利用可能する
			* 引数として渡す際に有効である反面、実行速度とメモリー効率を犠牲にする
		"""
		instance = CSP.new(Json())
		jsons, entries = self._isolate_entries(instance)
		instance.on._jsons = jsons
		instance.on._entries = entries
		return instance

	def _isolate_entries(self, new_root: 'CSP[Json]') -> 'tuple[list[CSP[Json]], list[JsonEntry]]':
		"""自身を含めた全ての下位要素を新たなエントリーとして生成

		Args:
			new_root (CSP[Json]): ルートオブジェクト
		Returns:
			tuple[list[CSP[Json]], list[JsonEntry]: JSON, JSONエントリーリスト
		"""
		jsons: list[CSP[Json]] = []
		entries: list[JsonEntry] = []
		ids = self._relayed_entry_ids(self._entry_id)
		for new_entry_id, entry_id in enumerate(ids):
			entry = self.root.on._entries[entry_id]
			new_path = entry.path[len(self.path) + 1:] if new_entry_id > 0 else ''
			jsons.append(new_root.on._make_for_entry(new_entry_id))
			entries.append(JsonEntry.make(new_path, entry.entry_type, entry.entity))

		return jsons, entries

	def _relayed_entry_ids(self, entry_id: int) -> list[int]:
		"""指定位置のJSONエントリーを含めた全ての下位要素のエントリーIDを抽出

		Args:
			entry_id (int): エントリーID
		Returns:
			list[int]: エントリーIDリスト
		"""
		ids: list[int] = []
		remain = len(self.root.on._entries) - entry_id
		for i in range(remain):
			in_entry_id = i + self._entry_id
			path = self.root.on._entries[in_entry_id].path
			if self._starts_with(path, self.path):
				ids.append(in_entry_id)

		return ids

	def _starts_with(self, string: str, prefix: str) -> bool:
		"""文字列が接頭辞から始まるか判定

		Args:
			string (str): 文字列
			prefix (str): 接頭辞
		Returns:
			bool: True = 適合
		Note:
			XXX C++だと空文字を全く検証せず、ルート要素との比較をスキップしてしまうため、互換用に用意
		"""
		return len(prefix) == 0 or string.startswith(prefix)

	def to_string(self) -> str:
		"""文字列表現を取得

		Returns:
			str: 文字列表現
		"""
		if self.scalar_with(JsonEntryTypes.Boolean):
			return 'true' if self.as_bool else 'false'
		elif self.scalar_with(JsonEntryTypes.Number):
			return str(self.as_number)
		elif self.scalar_with(JsonEntryTypes.String):
			return '\"{text}\"'.format(text=String.escape(self.as_string, char('"')))
		elif self.scalar_with(JsonEntryTypes.Array):
			values = [under.on.to_string() for under in self.unders()]
			join_values = ','.join(values)
			return '[' + join_values + ']'
		else:
			values = ['\"{key}\":{value}'.format(key=under.on.symbol, value=under.on.to_string()) for under in self.unders()]
			join_values = ','.join(values)
			return '{' + join_values + '}'
