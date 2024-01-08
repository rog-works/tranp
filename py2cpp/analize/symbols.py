from typing import NamedTuple, TypeAlias

from py2cpp.analize.db import SymbolDB, SymbolRow
from py2cpp.analize.procedure import Procedure
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
import py2cpp.node.definition as defs
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node

Symbolic: TypeAlias = defs.Symbol | defs.Reference | defs.Type | defs.Literal | defs.ClassKind
Primitives: TypeAlias = int | str | bool | tuple | list | dict | None

PairSchema = NamedTuple('PairSchema', [('row', SymbolRow), ('first', SymbolRow), ('second', SymbolRow)])
ListSchema = NamedTuple('ListSchema', [('row', SymbolRow), ('value', SymbolRow)])
DictSchema = NamedTuple('DictSchema', [('row', SymbolRow), ('key', SymbolRow), ('value', SymbolRow)])


class SymbolSchema:
	"""シンボルスキーマ

	Attributes:
		__row (SymbolRow): 型のシンボルデータ
		__attrs (dict[str, SymbolRow]): キーと型の属性のシンボルデータのマップ情報
	"""

	def __init__(self, row: SymbolRow, **attrs: SymbolRow) -> None:
		"""インスタンスを生成

		Args:
			row (SymbolRow): 型のシンボルデータ
			**attrs (SymbolRow): キーと型の属性のシンボルデータのマップ情報
		"""
		self.__row = row
		self.__attrs = attrs

	@property
	def row(self) -> SymbolRow:
		"""SymbolRow: 型のシンボルデータ"""
		return self.__row

	def has_attr(self, key: str) -> bool:
		"""指定のキーの属性を持つか判定

		Args:
			key (str): キー
		Returns:
			bool: True = 所持
		"""
		return key in self.__attrs

	def __getattr__(self, key: str) -> SymbolRow:
		"""キーに対応する属性を取得

		Args:
			key (str): キー
		Returns:
			SymbolRow: 属性の型のシンボルデータ
		"""
		if self.has_attr(key):
			return self.__attrs[key]

		raise ValueError(f'Undefined key. key: {key}')

	def extends(self, **attrs: SymbolRow) -> 'SymbolSchema':
		"""既存のスキーマに属性を追加してインスタンスを生成

		Args:
			**attrs (SymbolRow): キーと型の属性のシンボルデータのマップ情報
		Returns:
			SymbolSchema: インスタンス
		"""
		return SymbolSchema(self.row, **attrs)


class Symbols:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, db: SymbolDB, module_path: ModulePath) -> None:
		"""インスタンスを生成

		Args:
			db (SymbolDB): シンボルテーブル
		"""
		self.__db = db
		self.__module_path = module_path

	def primitive_of(self, primitive_type: type[Primitives]) -> SymbolSchema:
		"""プリミティブ型のシンボルを解決

		Args:
			primitive_type (type[Primitives]): プリミティブ型
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のタイプを指定
		"""
		symbol_name = primitive_type.__name__ if primitive_type is not None else 'None'
		candidate = DSN.join(self.__module_path.ref_name, symbol_name)
		if candidate in self.__db.rows:
			return SymbolSchema(self.__db.rows[candidate])

		raise LogicError(f'Primitive not defined. name: {primitive_type.__name__}')

	def unknown_of(self) -> SymbolSchema:
		"""Unknown型のシンボルを解決

		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: Unknown型が未定義
		"""
		# XXX 'Unknown'の定数化を検討
		candidate = DSN.join(self.__module_path.ref_name, 'Unknown')
		if candidate in self.__db.rows:
			return SymbolSchema(self.__db.rows[candidate])

		raise LogicError(f'Unknown not defined.')

	def symbol_of(self, symbol: defs.Symbol) -> SymbolSchema:
		"""シンボルノードからシンボルを解決

		Args:
			symbol (Symbol): シンボルノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(symbol)

	def var_ref_of(self, var_ref: defs.Name) -> SymbolSchema:
		"""変数参照ノードからシンボルを解決

		Args:
			var_ref (Name): 変数参照ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(var_ref)

	def type_of(self, types: defs.Type) -> SymbolSchema:
		"""型ノードからシンボルを解決

		Args:
			types (Type): 型ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(types)

	def literal_of(self, literal: defs.Literal) -> SymbolSchema:
		"""リテラルノードからシンボルを解決

		Args:
			literal (Literal): リテラルノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(literal)

	def class_of(self, decl_class: defs.ClassKind) -> SymbolSchema:
		"""クラス定義ノードからシンボルを解決

		Args:
			decl_class (ClassKind): クラス定義ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(decl_class)

	def property_of(self, decl_class: defs.ClassKind, prop: defs.Name) -> SymbolSchema:
		"""クラス定義ノードと名前ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassKind): クラス定義ノード
			prop (Name): 名前ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(decl_class, prop.tokens)

	def result_of(self, expression: Node) -> SymbolSchema:
		"""式ノードからシンボルを解決

		Args:
			expression (Node): 式ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		handler = Handler(self)
		for node in expression.calculated():
			handler.process(node)

		# XXX 自分自身が含まれないため個別に実行
		handler.process(expression)

		return handler.result()

	def by(self, node: Node) -> SymbolSchema:
		"""シンボル系/式ノードからシンボルを解決

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: シンボルの解決に失敗
			LogicError: 引数にRelayを指定
		Note:
			XXX Relayは単体でシンボルを表さないため、このメソッドでは非対応とする
		"""
		if isinstance(node, defs.Relay):
			raise LogicError(f'Not supported node. node: {node}')

		if isinstance(node, defs.Symbol):
			return self.symbol_of(node)
		elif isinstance(node, defs.Name):
			return self.var_ref_of(node)
		elif isinstance(node, defs.Type):
			return self.type_of(node)
		elif isinstance(node, defs.ClassKind):
			return self.class_of(node)
		elif isinstance(node, defs.Literal):
			return self.literal_of(node)
		else:
			return self.result_of(node)

	def __resolve_symbol(self, symbolic: Symbolic, prop_name: str = '') -> SymbolSchema:
		"""シンボル系ノードからシンボルデータを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		found_row = self.__resolve_symbol_row(symbolic, prop_name)
		if found_row is not None:
			return SymbolSchema(found_row)

		raise LogicError(f'Symbol not defined. symbolic: {symbolic}, prop_name: {prop_name}')

	def __resolve_symbol_row(self, symbolic: Symbolic, prop_name: str) -> SymbolRow | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		symbol_row = self.__find_symbol_row(symbolic, prop_name)
		if symbol_row is None and symbolic.is_a(defs.Class):
			symbol_row = self.__resolve_symbol_row_recursive(symbolic.as_a(defs.Class), prop_name)

		return symbol_row

	def __resolve_symbol_row_recursive(self, decl_class: defs.Class, prop_name: str) -> SymbolRow | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			decl_class (Class): クラス定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		for parent_type in decl_class.parents:
			parent_type_row = self.__find_symbol_row(parent_type)
			if parent_type_row is None:
				break

			found_row = self.__resolve_symbol_row(parent_type_row.types, prop_name)
			if found_row:
				return found_row

		return None

	def __find_symbol_row(self, symbolic: Symbolic, prop_name: str = '') -> SymbolRow | None:
		"""シンボルデータを検索。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		domain_id = DSN.join(symbolic.domain_id, prop_name)
		domain_name = DSN.join(symbolic.domain_name, prop_name)
		if domain_id in self.__db.rows:
			return self.__db.rows[domain_id]
		elif domain_name in self.__db.rows:
			return self.__db.rows[domain_name]

		return None


class Handler(Procedure[SymbolSchema]):
	def __init__(self, symbols: Symbols) -> None:
		super().__init__()
		self._symbols = symbols

	# Fallback

	def on_fallback(self, node: Node) -> None:
		pass

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: SymbolSchema, var_type: SymbolSchema, value: SymbolSchema) -> SymbolSchema:
		return var_type

	# Primary

	def on_this_var(self, node: defs.ThisVar) -> SymbolSchema:
		return self._symbols.by(node)

	def on_param_this(self, node: defs.ParamThis) -> SymbolSchema:
		return self._symbols.by(node)

	def on_local_var(self, node: defs.LocalVar) -> SymbolSchema:
		return self._symbols.by(node)

	def on_class_type_name(self, node: defs.ClassTypeName) -> SymbolSchema:
		return self._symbols.by(node)

	def on_import_name(self, node: defs.ImportName) -> SymbolSchema:
		return self._symbols.by(node)

	def on_relay(self, node: defs.Relay, receiver: SymbolSchema) -> SymbolSchema:
		return self._symbols.property_of(receiver.row.types, node.property)

	def on_name(self, node: defs.Name) -> SymbolSchema:
		return self._symbols.by(node)

	def on_indexer(self, node: defs.Indexer, symbol: SymbolSchema, key: SymbolSchema) -> SymbolSchema:
		if isinstance(symbol.row.decl, (defs.AnnoAssign, defs.Parameter)):
			return self._symbols.by(symbol.row.decl.var_type)
		else:
			return self._symbols.by(symbol.row.decl.as_a(defs.MoveAssign).value)

	def on_general_type(self, node: defs.GeneralType) -> SymbolSchema:
		return self._symbols.by(node)

	def on_list_type(self, node: defs.ListType, symbol: SymbolSchema, value_type: SymbolSchema) -> SymbolSchema:
		return symbol.extends(value_type=value_type.row)

	def on_dict_type(self, node: defs.DictType, symbol: SymbolSchema, key_type: SymbolSchema, value_type: SymbolSchema) -> SymbolSchema:
		return symbol.extends(key_type=key_type.row, value_type=value_type.row)

	def on_union_type(self, node: defs.UnionType) -> SymbolSchema:
		raise LogicError(f'Operation not supoorted. {node}')

	def on_none_type(self, node: defs.NullType) -> SymbolSchema:
		return self._symbols.by(node)

	def on_func_call(self, node: defs.FuncCall, calls: SymbolSchema, arguments: list[SymbolSchema]) -> SymbolSchema:
		calls_function = calls.row.types.as_a(defs.Function)
		if calls_function.is_a(defs.Constructor):
			return self._symbols.by(calls_function.as_a(defs.Constructor).class_symbol)
		else:
			return self._symbols.by(calls_function.return_type.var_type)

	def on_super(self, node: defs.Super, calls: SymbolSchema, arguments: list[SymbolSchema]) -> SymbolSchema:
		return self._symbols.by(node.parent_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: SymbolSchema) -> SymbolSchema:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: SymbolSchema) -> SymbolSchema:
		return class_type

	# Operator

	def on_sum(self, node: defs.Sum, left: SymbolSchema, right: SymbolSchema) -> SymbolSchema:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.BinaryOperator, left: SymbolSchema, right: SymbolSchema, operator: str) -> SymbolSchema:
		methods = [method for method in left.row.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

		other = methods[0].parameters.pop()
		var_types = [other.var_type] if not other.var_type.is_a(defs.UnionType) else other.var_type.as_a(defs.UnionType).types
		for var_type in var_types:
			if self._symbols.by(var_type.one_of(defs.Symbol | defs.GenericType)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> SymbolSchema:
		return self._symbols.by(node)

	def on_float(self, node: defs.Float) -> SymbolSchema:
		return self._symbols.by(node)

	def on_string(self, node: defs.String) -> SymbolSchema:
		return self._symbols.by(node)

	def on_truthy(self, node: defs.Truthy) -> SymbolSchema:
		return self._symbols.by(node)

	def on_falsy(self, node: defs.Falsy) -> SymbolSchema:
		return self._symbols.by(node)

	def on_pair(self, node: defs.Pair, first: SymbolSchema, second: SymbolSchema) -> SymbolSchema:
		return self._symbols.by(node).extends(first=first.row, second=second.row)

	def on_list(self, node: defs.List, values: list[SymbolSchema]) -> SymbolSchema:
		if len(values) == 0:
			return self._symbols.by(node).extends(value=self._symbols.unknown_of().row)
		else:
			return self._symbols.by(node).extends(value=values[0].row)

	def on_dict(self, node: defs.Dict, items: list[PairSchema]) -> SymbolSchema:
		if len(items) == 0:
			return self._symbols.by(node).extends(key=self._symbols.unknown_of().row, value=self._symbols.unknown_of().row)
		else:
			return self._symbols.by(node).extends(key=items[0].first, value=items[0].second)
