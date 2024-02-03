from py2cpp.analyze.db import SymbolDB
from py2cpp.analyze.symbol import Primitives, SymbolRaw, SymbolResolver
from py2cpp.analyze.procedure import Procedure
import py2cpp.compatible.python.classes as classes
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.implementation import injectable
import py2cpp.node.definition as defs
from py2cpp.node.node import Node



class Symbols:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, db: SymbolDB) -> None:
		"""インスタンスを生成

		Args:
			db (SymbolDB): シンボルテーブル @inject
		"""
		self.__raws = db.raws

	def is_list(self, symbol: SymbolRaw) -> bool:
		"""シンボルがList型か判定

		Args:
			symbol (SymbolRaw): シンボル
		Return:
			bool: True = List型
		"""
		return symbol.types == self.type_of_primitive(list).types

	def is_dict(self, symbol: SymbolRaw) -> bool:
		"""シンボルがDict型か判定

		Args:
			symbol (SymbolRaw): シンボル
		Return:
			bool: True = Dict型
		"""
		return symbol.types == self.type_of_primitive(dict).types

	def from_fullyname(self, fullyname: str) -> SymbolRaw:
		"""完全参照名からシンボルを解決

		Args:
			fullyname (str): 完全参照名
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: 存在しないパスを指定
		"""
		if fullyname not in self.__raws:
			raise NotFoundError(f'SymbolRaw not defined. fullyname: {fullyname}')

		raw = self.__raws[fullyname]
		return self.type_of(raw.decl)

	def type_of_primitive(self, primitive_type: type[Primitives] | None) -> SymbolRaw:
		"""プリミティブ型のシンボルを解決

		Args:
			primitive_type (type[Primitives] | None): プリミティブ型
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のタイプを指定
		"""
		return SymbolResolver.by_primitive(self.__raws, primitive_type)

	def type_of_property(self, decl_class: defs.ClassDef, prop: defs.Var) -> SymbolRaw:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassDef): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		symbol = self.resolve(decl_class, prop.tokens)
		return self.__post_type_of_var(prop, symbol)

	def type_of(self, node: Node) -> SymbolRaw:
		"""シンボル系/式ノードからシンボルを解決 XXX 万能過ぎるので細分化を検討

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			SymbolRaw: シンボル
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

	def type_of_var(self, node: defs.Declable | defs.Reference) -> SymbolRaw:
		"""シンボル宣言・参照ノードのシンボルを解決

		Args:
			node (Declable | Reference): シンボル宣言・参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		symbol = self.resolve(node)
		return self.__post_type_of_var(node, symbol)

	def __post_type_of_var(self, node: defs.Declable | defs.Reference, symbol: SymbolRaw) -> SymbolRaw:
		"""シンボル宣言・参照ノードのシンボル解決の後処理

		Args:
			node (Declable | Reference): シンボル宣言・参照ノード XXX 未使用
			symbol (SymbolRaw): シンボル
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		Note:
			# このメソッドの目的
			* MoveAssignの宣言型の解決(シンボル宣言・参照ノード由来)
			@see resolve
		"""
		decl = symbol.decl
		if isinstance(decl, (defs.AnnoAssign, defs.Parameter)):
			return symbol
		elif isinstance(decl, defs.MoveAssign):
			return self.__resolve_procedural(decl.value)
		elif isinstance(decl, (defs.For, defs.Catch)):
			return self.__from_flow(decl)
		else:
			# defs.ClassDef
			return symbol

	def __from_declable(self, node: defs.Declable) -> SymbolRaw:
		"""シンボル宣言ノードからシンボルを解決

		Args:
			node (Declable): シンボル宣言ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.type_of_var(node)

	def __from_reference(self, node: defs.Reference) -> SymbolRaw:
		"""シンボル参照ノードからシンボルを解決

		Args:
			node (Reference): 参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		if isinstance(node, defs.Var):
			return self.type_of_var(node)
		else:
			# defs.Relay
			return self.__resolve_procedural(node)

	def __from_type(self, node: defs.Type) -> SymbolRaw:
		"""型ノードからシンボルを解決

		Args:
			node (Type): 型ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.resolve(node)

	def __from_literal(self, node: defs.Literal) -> SymbolRaw:
		"""リテラルノードからシンボルを解決

		Args:
			node (Literal): リテラルノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.__resolve_procedural(node)

	def __from_class(self, node: defs.ClassDef) -> SymbolRaw:
		"""クラス定義ノードからシンボルを解決

		Args:
			node (ClassDef): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		return self.resolve(node)

	def __from_flow(self, node: defs.For | defs.Catch) -> SymbolRaw:
		"""制御構文ノードからシンボルを解決

		Args:
			node (For | Catch): 制御構文ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		if isinstance(node, defs.For):
			return self.__resolve_procedural(node.for_in)
		else:
			# defs.Catch
			return self.__from_type(node.var_type)

	def __resolve_procedural(self, node: Node) -> SymbolRaw:
		"""ノードを展開してシンボルを解決

		Args:
			node (Node): ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		resolver = ProceduralResolver(self)
		for in_node in node.calculated():
			resolver.process(in_node)

		# XXX 自分自身が含まれないため個別に実行
		resolver.process(node)

		return resolver.result()

	def resolve(self, symbolic: defs.Symbolic, prop_name: str = '') -> SymbolRaw:
		"""シンボルテーブルからシンボルを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: シンボルの解決に失敗
		Note:
			# 注意点
			シンボルテーブルから直接解決するため、以下のシンボル解決は含まれない
			* MoveAssignの左辺の型の解決(シンボル宣言・参照ノード由来)
			@see __post_type_of_var
		"""
		found_raw = self.__resolve_raw(symbolic, prop_name)
		if found_raw is not None:
			return found_raw

		raise LogicError(f'SymbolRaw not defined. symbolic: {symbolic.fullyname}, prop_name: {prop_name}')

	def __resolve_raw(self, symbolic: defs.Symbolic, prop_name: str) -> SymbolRaw | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		symbol_raw = SymbolResolver.find_by_symbolic(self.__raws, symbolic, prop_name)
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
			inherit_type_raw = SymbolResolver.by_symbolic(self.__raws, inherit_type)
			found_raw = self.__resolve_raw(inherit_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		return None


class ProceduralResolver(Procedure[SymbolRaw]):
	def __init__(self, symbols: Symbols) -> None:
		super().__init__(verbose=False)
		self.symbols = symbols

	# Fallback

	def on_fallback(self, node: Node) -> None:
		pass

	# Statement compound

	def on_for_in(self, node: defs.ForIn, iterates: SymbolRaw) -> SymbolRaw:
		methods = {method.symbol.tokens: method for method in iterates.types.as_a(defs.Class).methods if method.symbol.tokens in ['__next__', '__iter__']}
		if '__next__' in methods:
			return self.symbols.resolve(methods['__next__'].return_type)
		else:
			return self.symbols.resolve(methods['__iter__'].return_type.as_a(defs.GenericType).primary_type)

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: SymbolRaw, var_type: SymbolRaw, default_value: SymbolRaw) -> SymbolRaw:
		return symbol

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: SymbolRaw, var_type: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return receiver

	def on_move_assign(self, node: defs.MoveAssign, receiver: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return receiver

	def on_aug_assign(self, node: defs.AugAssign, receiver: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		"""Note: XXX operatorに型はないので引数からは省略。on_fallbackによってpassされるのでスタックはズレない"""
		return receiver

	# Primary

	def on_decl_class_var(self, node: defs.DeclClassVar) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_decl_this_var(self, node: defs.DeclThisVar) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_decl_class_param(self, node: defs.DeclClassParam) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_decl_this_param(self, node: defs.DeclThisParam) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_types_name(self, node: defs.TypesName) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_import_name(self, node: defs.ImportName) -> SymbolRaw:
		return self.symbols.type_of_var(node)

	def on_relay(self, node: defs.Relay, receiver: SymbolRaw) -> SymbolRaw:
		return self.symbols.type_of_property(receiver.types, node.prop).refnize(node)

	def on_class_ref(self, node: defs.ClassRef) -> SymbolRaw:
		return self.symbols.type_of_var(node).refnize(node)

	def on_this_ref(self, node: defs.ThisRef) -> SymbolRaw:
		return self.symbols.type_of_var(node).refnize(node)

	def on_argument_label(self, node: defs.ArgumentLabel) -> SymbolRaw:
		func_symbol = self.symbols.type_of(node.invoker.calls)
		for param in func_symbol.types.as_a(defs.Function).parameters:
			if param.symbol.tokens == node.tokens:
				return self.symbols.type_of_var(param.symbol)

		raise LogicError(f'Parameter not defined. function: {func_symbol.types.fullyname}, label: {node.tokens}')

	def on_variable(self, node: defs.Var) -> SymbolRaw:
		return self.symbols.type_of_var(node).refnize(node)

	def on_indexer(self, node: defs.Indexer, receiver: SymbolRaw, key: SymbolRaw) -> SymbolRaw:
		if self.symbols.is_list(receiver):
			return receiver.attrs[0]
		elif self.symbols.is_dict(receiver):
			return receiver.attrs[1]
		else:
			raise ValueError(f'Not supported indexer symbol type. {str(receiver)}')

	def on_general_type(self, node: defs.GeneralType) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_list_type(self, node: defs.ListType, type_name: SymbolRaw, value_type: SymbolRaw) -> SymbolRaw:
		return type_name

	def on_dict_type(self, node: defs.DictType, type_name: SymbolRaw, key_type: SymbolRaw, value_type: SymbolRaw) -> SymbolRaw:
		return type_name

	def on_custom_type(self, node: defs.CustomType, type_name: SymbolRaw, template_types: list[SymbolRaw]) -> SymbolRaw:
		return type_name

	def on_union_type(self, node: defs.UnionType, type_name: SymbolRaw, or_types: list[SymbolRaw]) -> SymbolRaw:
		return type_name

	def on_null_type(self, node: defs.NullType) -> SymbolRaw:
		return self.symbols.type_of_primitive(None)

	def on_func_call(self, node: defs.FuncCall, calls: SymbolRaw, arguments: list[SymbolRaw]) -> SymbolRaw:
		if isinstance(calls.types, defs.Constructor):
			return self.symbols.type_of_var(calls.types.class_types.symbol)
		elif isinstance(calls.types, defs.Function):
			return calls.attrs[-1]
		else:
			# defs.ClassDef
			return calls

	def on_super(self, node: defs.Super, calls: SymbolRaw, arguments: list[SymbolRaw]) -> SymbolRaw:
		return self.symbols.resolve(node.super_class_symbol)

	def on_argument(self, node: defs.Argument, label: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: SymbolRaw) -> SymbolRaw:
		return class_type

	# Operator

	def on_factor(self, node: defs.Sum, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_not_compare(self, node: defs.NotCompare, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_or_compare(self, node: defs.OrCompare, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_and_compare(self, node: defs.AndCompare, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_comparison(self, node: defs.Comparison, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
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

	def on_or_bitwise(self, node: defs.OrBitwise, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_xor_bitwise(self, node: defs.XorBitwise, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__xor__')

	def on_and_bitwise(self, node: defs.AndBitwise, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_shift_bitwise(self, node: defs.Sum, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'<<': '__lshift__',
			'>>': '__rshift__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_sum(self, node: defs.Sum, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'+': '__add__',
			'-': '__sub__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_term(self, node: defs.Term, left: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'*': '__mul__',
			'/': '__truediv__',
			'%': '__mod__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def each_binary_operator(self, node: defs.BinaryOperator, left: SymbolRaw, right: list[SymbolRaw], operator: str) -> SymbolRaw:
		symbol = self.on_binary_operator(node, left, right[0], operator)
		for in_right in right[1:]:
			symbol = self.on_binary_operator(node, symbol, in_right, operator)

		return symbol

	def on_binary_operator(self, node: defs.BinaryOperator, left: SymbolRaw, right: SymbolRaw, operator: str) -> SymbolRaw:
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

	def on_integer(self, node: defs.Integer) -> SymbolRaw:
		return self.symbols.type_of_primitive(int)

	def on_float(self, node: defs.Float) -> SymbolRaw:
		return self.symbols.type_of_primitive(float)

	def on_string(self, node: defs.String) -> SymbolRaw:
		return self.symbols.type_of_primitive(str)

	def on_comment(self, node: defs.Comment) -> SymbolRaw:
		return self.symbols.type_of_primitive(str)

	def on_truthy(self, node: defs.Truthy) -> SymbolRaw:
		return self.symbols.type_of_primitive(bool)

	def on_falsy(self, node: defs.Falsy) -> SymbolRaw:
		return self.symbols.type_of_primitive(bool)

	def on_pair(self, node: defs.Pair, first: SymbolRaw, second: SymbolRaw) -> SymbolRaw:
		return self.symbols.type_of_primitive(classes.Pair).literalize(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[SymbolRaw]) -> SymbolRaw:
		value_type = values[0] if len(values) > 0 else self.symbols.type_of_primitive(classes.Unknown)
		return self.symbols.type_of_primitive(list).literalize(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[SymbolRaw]) -> SymbolRaw:
		if len(items) == 0:
			unknown_type = self.symbols.type_of_primitive(classes.Unknown)
			return self.symbols.type_of_primitive(dict).literalize(node).extends(unknown_type, unknown_type)
		else:
			key_type, value_type = items[0].attrs
			return self.symbols.type_of_primitive(dict).literalize(node).extends(key_type, value_type)

	# Terminal

	def on_group(self, node: defs.Group, expression: SymbolRaw) -> SymbolRaw:
		return expression

	# Terminal

	def on_empty(self, node: defs.Empty) -> SymbolRaw:
		# XXX 厳密にいうとNullとEmptyは別だが、実用上はほぼ同じなので代用
		return self.symbols.type_of_primitive(None)
