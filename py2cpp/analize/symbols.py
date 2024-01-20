from typing import TypeAlias

from py2cpp.analize.db import SymbolDB, SymbolRaw
from py2cpp.analize.procedure import Procedure
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable, override
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

	@override
	def __eq__(self, __value: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			__value (object): 比較対象
		Returns:
			bool: True = 同じ
		"""
		if type(__value) is not Symbol:
			return super().__eq__(__value)

		return __value.__repr__() == self.__repr__()

	@override
	def __repr__(self) -> str:
		"""オブジェクトの文字列表現を取得

		Returns:
			str: 文字列表現
		"""
		data = {
			'types': str(self.types),
			'attrs': [attr.__repr__() for attr in self.attrs],
		}
		return str(data)


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

	def type_of_primitive(self, primitive_type: type[Primitives]) -> Symbol:
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

	def type_of_unknown(self) -> Symbol:
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

	def type_of_property(self, decl_class: defs.ClassKind, prop: defs.Var) -> Symbol:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassKind): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		symbol = self.resolve(decl_class, prop.tokens)
		return self.__post_type_of_var(prop, symbol)

	def type_of(self, node: Node) -> Symbol:
		"""シンボル系/式ノードからシンボルを解決 XXX 万能過ぎるので細分化を検討

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		if isinstance(node, defs.Declable):
			return self.__from_declable(node)
		elif isinstance(node, defs.Reference):
			return self.__from_reference(node)
		elif isinstance(node, defs.Type):
			return self.__from_type(node)
		elif isinstance(node, defs.ClassKind):
			return self.__from_class(node)
		elif isinstance(node, defs.Literal):
			return self.__from_literal(node)
		else:
			return self.__resolve_procedural(node)

	def type_of_var(self, node: defs.Declable | defs.Reference) -> Symbol:
		"""シンボル宣言・参照ノードのシンボルを解決

		Args:
			node (Declable | Reference): シンボル宣言・参照ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		symbol = self.resolve(node)
		return self.__post_type_of_var(node, symbol)

	def __post_type_of_var(self, node: defs.Declable | defs.Reference, symbol: Symbol) -> Symbol:
		"""シンボル宣言・参照ノードのシンボル解決の後処理

		Args:
			node (Declable | Reference): シンボル宣言・参照ノード XXX 未使用
			symbol (Symbol): シンボル
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		Note:
			# このメソッドの目的
			* Generic型のサブタイプの解決(シンボル宣言・参照ノード由来)
			* MoveAssignの左辺の型の解決(シンボル宣言・参照ノード由来)
			@see resolve
		"""
		decl = symbol.raw.decl
		if isinstance(decl, (defs.AnnoAssign, defs.Parameter)):
			return self.__from_type(decl.var_type) if isinstance(decl.var_type, defs.GenericType) else symbol
		elif isinstance(decl, defs.MoveAssign):
			return self.__resolve_procedural(decl.value)
		# defs.ClassKind
		else:
			return symbol

	def __from_declable(self, node: defs.Declable) -> Symbol:
		"""シンボル宣言ノードからシンボルを解決

		Args:
			node (Declable): シンボル宣言ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.type_of_var(node)

	def __from_reference(self, node: defs.Reference) -> Symbol:
		"""シンボル参照ノードからシンボルを解決

		Args:
			node (Reference): 参照ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		if isinstance(node, defs.Var):
			return self.type_of_var(node)
		# defs.Relay
		else:
			return self.__resolve_procedural(node)

	def __from_type(self, node: defs.Type) -> Symbol:
		"""型ノードからシンボルを解決

		Args:
			node (Type): 型ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_procedural(node)

	def __from_literal(self, node: defs.Literal) -> Symbol:
		"""リテラルノードからシンボルを解決

		Args:
			node (Literal): リテラルノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_procedural(node)

	def __from_class(self, node: defs.ClassKind) -> Symbol:
		"""クラス定義ノードからシンボルを解決

		Args:
			node (ClassKind): クラス定義ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.resolve(node)

	def __resolve_procedural(self, node: Node) -> Symbol:
		"""ノードを展開してシンボルを解決

		Args:
			node (Node): ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		resolver = ProceduralResolver(self)
		for in_node in node.calculated():
			resolver.process(in_node)

		# XXX 自分自身が含まれないため個別に実行
		resolver.process(node)

		return resolver.result()

	def resolve(self, symbolic: Symbolic, prop_name: str = '') -> Symbol:
		"""シンボルテーブルからシンボルを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		Note:
			# 注意点
			シンボルテーブルから直接解決するため、以下のシンボル解決は含まれない
			* Generic型のサブタイプの解決(シンボル宣言・参照ノード由来)
			* MoveAssignの左辺の型の解決(シンボル宣言・参照ノード由来)
			@see __post_type_of_var
		"""
		found_raw = self.__resolve_raw(symbolic, prop_name)
		if found_raw is not None:
			return Symbol(found_raw)

		raise LogicError(f'Symbol not defined. symbolic: {symbolic.domain_id}, prop_name: {prop_name}')

	def __resolve_raw(self, symbolic: Symbolic, prop_name: str) -> SymbolRaw | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		symbol_raw = self.__find_raw(symbolic, prop_name)
		if symbol_raw is None and symbolic.is_a(defs.Class):
			symbol_raw = self.__resolve_raw_recursive(symbolic.as_a(defs.Class), prop_name)

		return symbol_raw

	def __resolve_raw_recursive(self, decl_class: defs.Class, prop_name: str) -> SymbolRaw | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			decl_class (Class): クラス定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		for parent_type in decl_class.parents:
			parent_type_raw = self.__find_raw(parent_type)
			if parent_type_raw is None:
				break

			found_raw = self.__resolve_raw(parent_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		return None

	def __find_raw(self, symbolic: Symbolic, prop_name: str = '') -> SymbolRaw | None:
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


class ProceduralResolver(Procedure[Symbol]):
	def __init__(self, symbols: Symbols) -> None:
		super().__init__()
		self.symbols = symbols

	# Fallback

	def on_fallback(self, node: Node) -> None:
		pass

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: Symbol, var_type: Symbol, value: Symbol) -> Symbol:
		return var_type

	# Element

	def on_return_decl(self, node: defs.ReturnDecl, var_type: Symbol) -> Symbol:
		return var_type

	# Primary

	def on_class_decl_var(self, node: defs.ClassDeclVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_this_decl_var(self, node: defs.ThisDeclVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_param_class(self, node: defs.ParamClass) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_param_this(self, node: defs.ParamThis) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_local_decl_var(self, node: defs.LocalDeclVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_types_name(self, node: defs.TypesName) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_import_name(self, node: defs.ImportName) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_relay(self, node: defs.Relay, receiver: Symbol) -> Symbol:
		if isinstance(node.receiver, defs.Indexer):
			return self.symbols.type_of_property(receiver.attrs[0].types, node.prop)
		else:
			return self.symbols.type_of_property(receiver.types, node.prop)

	def on_class_var(self, node: defs.ClassVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_this_var(self, node: defs.ThisVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_variable(self, node: defs.Var) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_indexer(self, node: defs.Indexer, symbol: Symbol, key: Symbol) -> Symbol:
		return symbol

	def on_general_type(self, node: defs.GeneralType) -> Symbol:
		return self.symbols.resolve(node)

	def on_list_type(self, node: defs.ListType, symbol: Symbol, value_type: Symbol) -> Symbol:
		return symbol.extends(value_type)

	def on_dict_type(self, node: defs.DictType, symbol: Symbol, key_type: Symbol, value_type: Symbol) -> Symbol:
		return symbol.extends(key_type, value_type)

	def on_custom_type(self, node: defs.CustomType, symbol: Symbol, template_types: list[Symbol]) -> Symbol:
		return symbol.extends(*template_types)

	def on_union_type(self, node: defs.UnionType, symbol: Symbol, or_types: list[Symbol]) -> Symbol:
		return symbol.extends(*or_types)

	def on_null_type(self, node: defs.NullType) -> Symbol:
		return self.symbols.resolve(node)

	def on_func_call(self, node: defs.FuncCall, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		if isinstance(calls.types, defs.Constructor):
			return self.symbols.type_of_var(calls.types.class_symbol)
		elif isinstance(calls.types, defs.Function):
			return self.symbols.resolve(calls.types.return_decl.var_type)
		# defs.ClassKind
		else:
			return calls

	def on_super(self, node: defs.Super, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		return self.symbols.resolve(node.parent_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: Symbol) -> Symbol:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: Symbol) -> Symbol:
		return class_type

	# Operator

	def on_factor(self, node: defs.Sum, value: Symbol) -> Symbol:
		return value

	def on_not_compare(self, node: defs.NotCompare, value: Symbol) -> Symbol:
		return value

	def on_or_compare(self, node: defs.OrCompare, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__or__')

	def on_and_compare(self, node: defs.AndCompare, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__and__')

	def on_comparison(self, node: defs.Comparison, left: Symbol, right: Symbol) -> Symbol:
		operators = {
			'==': '__eq__',
			'<': '__lt__',
			'>': '__gt__',
			'<=': '__le__',
			'>=': '__ge__',
			'<>': '__not__',
			'!=': '__not__',
			'in': '__contains__',
			'not.in': '__contains__',  # XXX 型推論的に同じなので代用
			'is': '__eq__',  # XXX 型推論的に同じなので代用
			'is.not': '__eq__',  # XXX 型推論的に同じなので代用
		}
		return self.on_binary_operator(node, left, right, '__eq__')

	def on_or_bitwise(self, node: defs.OrBitwise, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__or__')

	def on_xor_bitwise(self, node: defs.XorBitwise, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__xor__')

	def on_and_bitwise(self, node: defs.AndBitwise, left: Symbol, right: Symbol) -> Symbol:
		return self.on_binary_operator(node, left, right, '__and__')

	def on_shift_bitwise(self, node: defs.Sum, left: Symbol, right: Symbol) -> Symbol:
		operators = {
			'<<': '__lshift__',
			'>>': '__rshift__',
		}
		return self.on_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_sum(self, node: defs.Sum, left: Symbol, right: Symbol) -> Symbol:
		operators = {
			'+': '__add__',
			'-': '__sub__',
		}
		return self.on_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_term(self, node: defs.Term, left: Symbol, right: Symbol) -> Symbol:
		operators = {
			'*': '__mul__',
			'/': '__truediv__',
			'%': '__mod__',
		}
		return self.on_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_binary_operator(self, node: defs.BinaryOperator, left: Symbol, right: Symbol, operator: str) -> Symbol:
		methods = [method for method in left.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left.types.domain_id}, {right.types.domain_id}, {operator}')

		other = methods[0].parameters.pop()
		var_types = other.var_type.or_types if isinstance(other.var_type, defs.UnionType) else [other.var_type]
		for var_type in var_types:
			if self.symbols.resolve(var_type.as_a(defs.Type)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left.types.domain_id}, {right.types.domain_id}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> Symbol:
		return self.symbols.resolve(node)

	def on_float(self, node: defs.Float) -> Symbol:
		return self.symbols.resolve(node)

	def on_string(self, node: defs.String) -> Symbol:
		return self.symbols.resolve(node)

	def on_truthy(self, node: defs.Truthy) -> Symbol:
		return self.symbols.resolve(node)

	def on_falsy(self, node: defs.Falsy) -> Symbol:
		return self.symbols.resolve(node)

	def on_pair(self, node: defs.Pair, first: Symbol, second: Symbol) -> Symbol:
		return self.symbols.resolve(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[Symbol]) -> Symbol:
		value_type = values[0] if len(values) > 0 else self.symbols.type_of_unknown()
		return self.symbols.resolve(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[Symbol]) -> Symbol:
		if len(items) == 0:
			unknown_type = self.symbols.type_of_unknown()
			return self.symbols.resolve(node).extends(unknown_type, unknown_type)
		else:
			key_type, value_type = items[0].attrs
			return self.symbols.resolve(node).extends(key_type, value_type)
