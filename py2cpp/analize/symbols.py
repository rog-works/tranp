from typing import NamedTuple, TypeAlias

from py2cpp.analize.db import SymbolDB, SymbolRaw
from py2cpp.analize.procedure import Procedure
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

Symbolic: TypeAlias = defs.Declable | defs.Reference | defs.Type | defs.Literal | defs.ClassKind
Primitives: TypeAlias = int | str | bool | tuple | list | dict | None


class Symbol:
	"""シンボル"""

	def __init__(self, raw: SymbolRaw, *attrs: 'Symbol') -> None:
		"""インスタンスを生成

		Args:
			raw (SymbolRaw): 型のシンボルデータ
			*attrs (Symbol): 属性シンボルリスト
		"""
		self.types = raw.types
		self.attrs = list(attrs)
		self.raw = raw

	def extends(self, *attrs: 'Symbol') -> 'Symbol':
		"""既存のスキーマに属性を追加してインスタンスを生成

		Args:
			*attrs (Symbol): 属性シンボルリスト
		Returns:
			Symbol: インスタンス
		"""
		return Symbol(self.raw, *[*self.attrs, *attrs])


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

	def primitive_of(self, primitive_type: type[Primitives]) -> Symbol:
		"""プリミティブ型のシンボルを解決

		Args:
			primitive_type (type[Primitives]): プリミティブ型
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のタイプを指定
		"""
		symbol_name = primitive_type.__name__ if primitive_type is not None else 'None'
		candidate = DSN.join(self.__module_path.ref_name, symbol_name)
		if candidate in self.__db.raws:
			return Symbol(self.__db.raws[candidate])

		raise LogicError(f'Primitive not defined. name: {primitive_type.__name__}')

	def unknown_of(self) -> Symbol:
		"""Unknown型のシンボルを解決

		Returns:
			Symbol: シンボル
		Raises:
			LogicError: Unknown型が未定義
		"""
		# XXX 'Unknown'の定数化を検討
		candidate = DSN.join(self.__module_path.ref_name, 'Unknown')
		if candidate in self.__db.raws:
			return Symbol(self.__db.raws[candidate])

		raise LogicError(f'Unknown not defined.')

	def property_of(self, decl_class: defs.ClassKind, prop: defs.Var) -> Symbol:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassKind): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_symbol(decl_class, prop.tokens)

	def type_of(self, node: Node) -> Symbol:
		"""シンボル系/式ノードからシンボルを解決

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		symbol = self.__type_of(node)
		decl = symbol.raw.decl
		if isinstance(decl, (defs.AnnoAssign, defs.Parameter)):
			if isinstance(decl.var_type, defs.ListType):
				return symbol.extends(self.type_of(decl.var_type.value_type))
			elif isinstance(decl.var_type, defs.DictType):
				return symbol.extends(self.type_of(decl.var_type.key_type), self.type_of(decl.var_type.value_type))
		elif isinstance(decl, defs.MoveAssign):
			return self.type_of(decl.value)

		return symbol

	def __type_of(self, node: Node) -> Symbol:
		"""シンボル系/式ノードからシンボルを解決

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.Declable):
			return self.__resolve_symbol(node)
		elif isinstance(node, defs.Var):
			return self.__resolve_symbol(node)
		elif isinstance(node, defs.Relay):
			# XXX Relayは実質的に式であるためresult_ofを使用
			return self.__from_expression(node)
		elif isinstance(node, defs.Type):
			return self.__resolve_symbol(node)
		elif isinstance(node, defs.ClassKind):
			return self.__resolve_symbol(node)
		elif isinstance(node, defs.Literal):
			return self.__resolve_symbol(node)
		else:
			return self.__from_expression(node)

	def __from_expression(self, expression: Node) -> Symbol:
		"""式ノードからシンボルを解決

		Args:
			expression (Node): 式ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		handler = Handler(self)
		for node in expression.calculated():
			handler.process(node)

		# XXX 自分自身が含まれないため個別に実行
		handler.process(expression)

		return handler.result()

	def __resolve_symbol(self, symbolic: Symbolic, prop_name: str = '') -> Symbol:
		"""シンボル系ノードからシンボルデータを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		found_raw = self.__resolve_symbol_raw(symbolic, prop_name)
		if found_raw is not None:
			return Symbol(found_raw)

		raise LogicError(f'Symbol not defined. symbolic: {symbolic}, prop_name: {prop_name}')

	def __resolve_symbol_raw(self, symbolic: Symbolic, prop_name: str) -> SymbolRaw | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		symbol_raw = self.__find_symbol_raw(symbolic, prop_name)
		if symbol_raw is None and symbolic.is_a(defs.Class):
			symbol_raw = self.__resolve_symbol_raw_recursive(symbolic.as_a(defs.Class), prop_name)

		return symbol_raw

	def __resolve_symbol_raw_recursive(self, decl_class: defs.Class, prop_name: str) -> SymbolRaw | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			decl_class (Class): クラス定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		for parent_type in decl_class.parents:
			parent_type_raw = self.__find_symbol_raw(parent_type)
			if parent_type_raw is None:
				break

			found_raw = self.__resolve_symbol_raw(parent_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		return None

	def __find_symbol_raw(self, symbolic: Symbolic, prop_name: str = '') -> SymbolRaw | None:
		"""シンボルデータを検索。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		domain_id = DSN.join(symbolic.domain_id, prop_name)
		domain_name = DSN.join(symbolic.domain_name, prop_name)
		if domain_id in self.__db.raws:
			return self.__db.raws[domain_id]
		elif domain_name in self.__db.raws:
			return self.__db.raws[domain_name]

		return None


class Handler(Procedure[Symbol]):
	def __init__(self, symbols: Symbols) -> None:
		super().__init__()
		self._symbols = symbols

	# Fallback

	def on_fallback(self, node: Node) -> None:
		pass

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: Symbol, var_type: Symbol, value: Symbol) -> Symbol:
		return var_type

	# Primary

	def on_class_var(self, node: defs.ClassVar) -> Symbol:
		return self._symbols.type_of(node)

	def on_this_var(self, node: defs.ThisVar) -> Symbol:
		return self._symbols.type_of(node)

	def on_param_class(self, node: defs.ParamClass) -> Symbol:
		return self._symbols.type_of(node)

	def on_param_this(self, node: defs.ParamThis) -> Symbol:
		return self._symbols.type_of(node)

	def on_local_var(self, node: defs.LocalVar) -> Symbol:
		return self._symbols.type_of(node)

	def on_types_name(self, node: defs.TypesName) -> Symbol:
		return self._symbols.type_of(node)

	def on_import_name(self, node: defs.ImportName) -> Symbol:
		return self._symbols.type_of(node)

	def on_relay(self, node: defs.Relay, receiver: Symbol) -> Symbol:
		return self._symbols.property_of(receiver.types, node.prop)

	def on_var(self, node: defs.Var) -> Symbol:
		return self._symbols.type_of(node)

	def on_indexer(self, node: defs.Indexer, symbol: Symbol, key: Symbol) -> Symbol:
		if isinstance(symbol.raw.decl, (defs.AnnoAssign, defs.Parameter)):
			return self._symbols.type_of(symbol.raw.decl.var_type.as_a(defs.CollectionType).value_type)
		else:
			return self._symbols.type_of(symbol.raw.decl.as_a(defs.MoveAssign).value)

	def on_general_type(self, node: defs.GeneralType) -> Symbol:
		return self._symbols.type_of(node)

	def on_list_type(self, node: defs.ListType, symbol: Symbol, value_type: Symbol) -> Symbol:
		return symbol.extends(value_type)

	def on_dict_type(self, node: defs.DictType, symbol: Symbol, key_type: Symbol, value_type: Symbol) -> Symbol:
		return symbol.extends(key_type, value_type)

	def on_union_type(self, node: defs.UnionType) -> Symbol:
		raise LogicError(f'Operation not supoorted. {node}')

	def on_none_type(self, node: defs.NullType) -> Symbol:
		return self._symbols.type_of(node)

	def on_func_call(self, node: defs.FuncCall, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		calls_function = calls.types.as_a(defs.Function)
		if calls_function.is_a(defs.Constructor):
			return self._symbols.type_of(calls_function.as_a(defs.Constructor).class_symbol)
		else:
			return self._symbols.type_of(calls_function.return_decl.var_type)

	def on_super(self, node: defs.Super, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		return self._symbols.type_of(node.parent_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: Symbol) -> Symbol:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: Symbol) -> Symbol:
		return class_type

	# Operator

	def on_sum(self, node: defs.Sum, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.BinaryOperator, left: Symbol, right: Symbol, operator: str) -> Symbol:
		methods = [method for method in left.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

		other = methods[0].parameters.pop()
		var_types = [other.var_type] if not other.var_type.is_a(defs.UnionType) else other.var_type.as_a(defs.UnionType).types
		for var_type in var_types:
			if self._symbols.type_of(var_type.one_of(defs.Declable | defs.GenericType)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> Symbol:
		return self._symbols.type_of(node)

	def on_float(self, node: defs.Float) -> Symbol:
		return self._symbols.type_of(node)

	def on_string(self, node: defs.String) -> Symbol:
		return self._symbols.type_of(node)

	def on_truthy(self, node: defs.Truthy) -> Symbol:
		return self._symbols.type_of(node)

	def on_falsy(self, node: defs.Falsy) -> Symbol:
		return self._symbols.type_of(node)

	def on_pair(self, node: defs.Pair, first: Symbol, second: Symbol) -> Symbol:
		return self._symbols.type_of(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[Symbol]) -> Symbol:
		value_type = values[0] if len(values) > 0 else self._symbols.unknown_of()
		return self._symbols.type_of(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[Symbol]) -> Symbol:
		if len(items) == 0:
			unknown_type = self._symbols.unknown_of()
			return self._symbols.type_of(node).extends(unknown_type, unknown_type)
		else:
			key_type, value_type = items[0].attrs
			return self._symbols.type_of(node).extends(key_type, value_type)
