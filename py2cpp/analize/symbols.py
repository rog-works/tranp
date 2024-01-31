from typing import TypeAlias

from py2cpp.analize.db import SymbolDB
from py2cpp.analize.symbol import Symbol, SymbolRaw
from py2cpp.analize.procedure import Procedure
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.implementation import injectable
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

Primitives: TypeAlias = int | str | bool | tuple | list | dict


class Symbols:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, module_path: ModulePath, db: SymbolDB) -> None:
		"""インスタンスを生成

		Args:
			module_path (ModulePath): モジュールパス
			db (SymbolDB): シンボルテーブル
		"""
		self.__raws = db.raws
		self.__module_path = module_path

	def is_list(self, symbol: Symbol) -> bool:
		"""シンボルがList型か判定

		Args:
			symbol (Symbol): シンボル
		Return:
			bool: True = List型
		"""
		return symbol.types == self.type_of_primitive(list).types

	def is_dict(self, symbol: Symbol) -> bool:
		"""シンボルがDict型か判定

		Args:
			symbol (Symbol): シンボル
		Return:
			bool: True = Dict型
		"""
		return symbol.types == self.type_of_primitive(dict).types

	def from_fullyname(self, fullyname: str) -> Symbol:
		"""参照フルパスからシンボルを解決

		Args:
			fullyname (str): 参照フルパス
		Returns:
			Symbol: シンボル
		Raises:
			NotFoundError: 存在しないパスを指定
		"""
		if fullyname not in self.__raws:
			raise NotFoundError(f'Symbol not defined. fullyname: {fullyname}')

		raw = self.__raws[fullyname]
		return self.type_of(raw.decl)

	def type_of_primitive(self, primitive_type: type[Primitives] | None) -> Symbol:
		"""プリミティブ型のシンボルを解決

		Args:
			primitive_type (type[Primitives] | None): プリミティブ型
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のタイプを指定
		"""
		symbol_name = primitive_type.__name__ if primitive_type is not None else 'None'
		candidate = DSN.join(self.__module_path.ref_name, symbol_name)
		if candidate in self.__raws:
			return Symbol(self.__raws[candidate])

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
		if candidate in self.__raws:
			return Symbol(self.__raws[candidate])

		raise LogicError(f'Unknown not defined.')

	def type_of_property(self, decl_class: defs.ClassDef, prop: defs.Var) -> Symbol:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassDef): クラス定義ノード
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
		elif isinstance(node, defs.ClassDef):
			return self.__from_class(node)
		elif isinstance(node, defs.Literal):
			return self.__from_literal(node)
		elif isinstance(node, (defs.For, defs.Catch)):
			return self.__from_flow(node)
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
			* MoveAssignの宣言型の解決(シンボル宣言・参照ノード由来)
			@see resolve
		"""
		decl = symbol.raw.decl
		if isinstance(decl, (defs.AnnoAssign, defs.Parameter)):
			return self.__from_type(decl.var_type) if isinstance(decl.var_type, defs.GenericType) else symbol
		elif isinstance(decl, defs.MoveAssign):
			return self.__resolve_procedural(decl.value)
		elif isinstance(decl, (defs.For, defs.Catch)):
			return self.__from_flow(decl)
		else:
			# defs.ClassDef
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
		else:
			# defs.Relay
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

	def __from_class(self, node: defs.ClassDef) -> Symbol:
		"""クラス定義ノードからシンボルを解決

		Args:
			node (ClassDef): クラス定義ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.resolve(node)

	def __from_flow(self, node: defs.For | defs.Catch) -> Symbol:
		"""制御構文ノードからシンボルを解決

		Args:
			node (For | Catch): 制御構文ノード
		Returns:
			Symbol: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		if isinstance(node, defs.For):
			return self.__resolve_procedural(node.for_in)
		else:
			# defs.Catch
			return self.__from_type(node.var_type)

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

	def resolve(self, symbolic: defs.Symbolic, prop_name: str = '') -> Symbol:
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

		raise LogicError(f'Symbol not defined. symbolic: {symbolic.fullyname}, prop_name: {prop_name}')

	def __resolve_raw(self, symbolic: defs.Symbolic, prop_name: str) -> SymbolRaw | None:
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
		for inherit_type in decl_class.inherits:
			inherit_type_raw = self.__find_raw(inherit_type)
			if inherit_type_raw is None:
				break

			found_raw = self.__resolve_raw(inherit_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		return None

	def __find_raw(self, symbolic: defs.Symbolic, prop_name: str = '') -> SymbolRaw | None:
		"""シンボルデータを検索。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		scopes = [DSN.left(symbolic.scope, DSN.elem_counts(symbolic.scope) - i) for i in range(DSN.elem_counts(symbolic.scope))]
		for scope in scopes:
			candidate = DSN.join(scope, symbolic.domain_name, prop_name)
			if candidate not in self.__raws:
				continue

			# XXX ローカル変数の参照は、クラス直下のスコープを参照できない
			if symbolic.is_a(defs.Var) and scope in self.__raws and self.__raws[scope].types.is_a(defs.Class):
				continue

			return self.__raws[candidate]

		return None


class ProceduralResolver(Procedure[Symbol]):
	def __init__(self, symbols: Symbols) -> None:
		super().__init__(verbose=False)
		self.symbols = symbols

	# Fallback

	def on_fallback(self, node: Node) -> None:
		pass

	# Statement compound

	def on_for_in(self, node: defs.ForIn, iterates: Symbol) -> Symbol:
		methods = {method.symbol.tokens: method for method in iterates.types.as_a(defs.Class).methods if method.symbol.tokens in ['__next__', '__iter__']}
		if '__next__' in methods:
			return self.symbols.resolve(methods['__next__'].return_type)
		else:
			return self.symbols.resolve(methods['__iter__'].return_type.as_a(defs.GenericType).primary_type)

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: Symbol, var_type: Symbol, value: Symbol) -> Symbol:
		return var_type

	def on_move_assign(self, node: defs.MoveAssign, receiver: Symbol, value: Symbol) -> Symbol:
		return receiver

	def on_aug_assign(self, node: defs.AugAssign, receiver: Symbol, value: Symbol) -> Symbol:
		"""Note: XXX operatorに型はないので引数からは省略"""
		return receiver

	# Primary

	def on_decl_class_var(self, node: defs.DeclClassVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_decl_this_var(self, node: defs.DeclThisVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_decl_class_param(self, node: defs.DeclClassParam) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_decl_this_param(self, node: defs.DeclThisParam) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_types_name(self, node: defs.TypesName) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_import_name(self, node: defs.ImportName) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_relay(self, node: defs.Relay, receiver: Symbol) -> Symbol:
		prop_symbol = self.symbols.type_of_property(receiver.types, node.prop)
		if isinstance(prop_symbol.types, defs.Method):
			# XXX 同じものを比較しているので意味がない
			receiver_ts = [self.symbols.resolve(t) for t in receiver.types.generic_types]
			prop_ts = [self.symbols.resolve(t) for t in prop_symbol.types.class_types.generic_types]
			attrs = [receiver.attrs[index] for index, t in enumerate(receiver_ts) if t in prop_ts]
			return prop_symbol.extends(*attrs)

		return prop_symbol

	def on_class_ref(self, node: defs.ClassRef) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_this_ref(self, node: defs.ThisRef) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_argument_label(self, node: defs.ArgumentLabel) -> Symbol:
		func_symbol = self.symbols.type_of(node.invoker.calls)
		for param in func_symbol.types.as_a(defs.Function).parameters:
			if param.symbol.tokens == node.tokens:
				return self.symbols.type_of_var(param.symbol)

		raise LogicError(f'Parameter not defined. function: {func_symbol.types.fullyname}, label: {node.tokens}')

	def on_variable(self, node: defs.Var) -> Symbol:
		return self.symbols.type_of_var(node)

	def on_indexer(self, node: defs.Indexer, receiver: Symbol, key: Symbol) -> Symbol:
		if self.symbols.is_list(receiver):
			return receiver.attrs[0]
		elif self.symbols.is_dict(receiver):
			return receiver.attrs[1]
		else:
			raise ValueError(f'Not supported indexer symbol type. {str(receiver)}')

	def on_general_type(self, node: defs.GeneralType) -> Symbol:
		return self.symbols.resolve(node)

	def on_list_type(self, node: defs.ListType, type_name: Symbol, value_type: Symbol) -> Symbol:
		return type_name.extends(value_type)

	def on_dict_type(self, node: defs.DictType, type_name: Symbol, key_type: Symbol, value_type: Symbol) -> Symbol:
		return type_name.extends(key_type, value_type)

	def on_custom_type(self, node: defs.CustomType, type_name: Symbol, template_types: list[Symbol]) -> Symbol:
		return type_name.extends(*template_types)

	def on_union_type(self, node: defs.UnionType, type_name: Symbol, or_types: list[Symbol]) -> Symbol:
		return type_name.extends(*or_types)

	def on_null_type(self, node: defs.NullType) -> Symbol:
		return self.symbols.resolve(node)

	def on_func_call(self, node: defs.FuncCall, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		if isinstance(calls.types, defs.Constructor):
			return self.symbols.type_of_var(calls.types.class_types.symbol)
		elif isinstance(calls.types, defs.Function):
			symbol = self.symbols.type_of(calls.types.return_type)
			# FIXME 一部のパターンにしか対応出来ていない
			if symbol.types.is_a(defs.TemplateClass):
				return calls.attrs[0]

			return symbol
		else:
			# defs.ClassDef
			return calls

	def on_super(self, node: defs.Super, calls: Symbol, arguments: list[Symbol]) -> Symbol:
		return self.symbols.resolve(node.super_class_symbol)

	def on_argument(self, node: defs.Argument, label: Symbol, value: Symbol) -> Symbol:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: Symbol) -> Symbol:
		return class_type

	# Operator

	def on_factor(self, node: defs.Sum, value: Symbol) -> Symbol:
		return value

	def on_not_compare(self, node: defs.NotCompare, value: Symbol) -> Symbol:
		return value

	def on_or_compare(self, node: defs.OrCompare, left: Symbol, right: list[Symbol]) -> Symbol:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_and_compare(self, node: defs.AndCompare, left: Symbol, right: list[Symbol]) -> Symbol:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_comparison(self, node: defs.Comparison, left: Symbol, right: list[Symbol]) -> Symbol:
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
		return self.each_binary_operator(node, left, right, '__eq__')

	def on_or_bitwise(self, node: defs.OrBitwise, left: Symbol, right: list[Symbol]) -> Symbol:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_xor_bitwise(self, node: defs.XorBitwise, left: Symbol, right: list[Symbol]) -> Symbol:
		return self.each_binary_operator(node, left, right, '__xor__')

	def on_and_bitwise(self, node: defs.AndBitwise, left: Symbol, right: list[Symbol]) -> Symbol:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_shift_bitwise(self, node: defs.Sum, left: Symbol, right: list[Symbol]) -> Symbol:
		operators = {
			'<<': '__lshift__',
			'>>': '__rshift__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_sum(self, node: defs.Sum, left: Symbol, right: list[Symbol]) -> Symbol:
		operators = {
			'+': '__add__',
			'-': '__sub__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_term(self, node: defs.Term, left: Symbol, right: list[Symbol]) -> Symbol:
		operators = {
			'*': '__mul__',
			'/': '__truediv__',
			'%': '__mod__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def each_binary_operator(self, node: defs.BinaryOperator, left: Symbol, right: list[Symbol], operator: str) -> Symbol:
		symbol = self.on_binary_operator(node, left, right[0], operator)
		for in_right in right[1:]:
			symbol = self.on_binary_operator(node, symbol, in_right, operator)

		return symbol

	def on_binary_operator(self, node: defs.BinaryOperator, left: Symbol, right: Symbol, operator: str) -> Symbol:
		methods = [method for method in left.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left.types.domain_name} {operator} {right.types.domain_name}')

		other = methods[0].parameters.pop()
		var_types = other.var_type.or_types if isinstance(other.var_type, defs.UnionType) else [other.var_type]
		for var_type in var_types:
			if self.symbols.resolve(var_type.as_a(defs.Type)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left.types.domain_name} {operator} {right.types.domain_name}')

	# Literal

	def on_integer(self, node: defs.Integer) -> Symbol:
		return self.symbols.resolve(node)

	def on_float(self, node: defs.Float) -> Symbol:
		return self.symbols.resolve(node)

	def on_string(self, node: defs.String) -> Symbol:
		return self.symbols.resolve(node)

	def on_comment(self, node: defs.Comment) -> Symbol:
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

	# Terminal

	def on_group(self, node: defs.Group, expression: Symbol) -> Symbol:
		return expression

	# Terminal

	def on_empty(self, node: defs.Empty) -> Symbol:
		# XXX 厳密にいうとNullとEmptyは別だが、実用上はほぼ同じなので代用
		return self.symbols.type_of_primitive(None)
