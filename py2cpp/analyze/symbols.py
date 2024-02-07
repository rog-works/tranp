from py2cpp.analyze.db import SymbolDB
from py2cpp.analyze.symbol import SymbolRaw
from py2cpp.analyze.procedure import Procedure
from py2cpp.analyze.finder import SymbolFinder
from py2cpp.ast.dsn import DSN
import py2cpp.compatible.python.classes as classes
from py2cpp.compatible.python.types import Primitives
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import implements, injectable
import py2cpp.lang.sequence as seqs
import py2cpp.node.definition as defs
from py2cpp.node.node import Node


class Symbols:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, db: SymbolDB, finder: SymbolFinder) -> None:
		"""インスタンスを生成

		Args:
			db (SymbolDB): シンボルテーブル @inject
			finder (SymbolFinder): シンボル検索 @inject
		"""
		self.__raws = db.raws
		self.__finder = finder

	def is_a(self, symbol: SymbolRaw, primitive_type: type[Primitives]) -> bool:
		"""シンボルの型を判定

		Args:
			symbol (SymbolRaw): シンボル
			primitive_type (type[Primitives]): プリミティブ型
		Return:
			bool: True = 指定の型と一致
		"""
		return symbol.types == self.type_of_primitive(primitive_type).types

	def from_fullyname(self, fullyname: str) -> SymbolRaw:
		"""完全参照名からシンボルを解決

		Args:
			fullyname (str): 完全参照名
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		return self.__finder.by(self.__raws, fullyname)

	def type_of_primitive(self, primitive_type: type[Primitives] | None) -> SymbolRaw:
		"""プリミティブ型のシンボルを解決

		Args:
			primitive_type (type[Primitives] | None): プリミティブ型
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		return self.__finder.by_primitive(self.__raws, primitive_type)

	def type_of_property(self, decl_class: defs.ClassDef, prop: defs.Var) -> SymbolRaw:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			decl_class (ClassDef): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		return self.resolve(decl_class, prop.tokens)

	def type_of(self, node: Node) -> SymbolRaw:
		"""シンボル系/式ノードからシンボルを解決 XXX 万能過ぎるので細分化を検討

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		if isinstance(node, defs.Declable):
			return self.resolve(node)
		elif isinstance(node, defs.Reference):
			return self.__from_reference(node)
		elif isinstance(node, defs.Type):
			return self.resolve(node)
		elif isinstance(node, defs.ClassDef):
			return self.resolve(node)
		elif isinstance(node, defs.Literal):
			return self.__resolve_procedural(node)
		elif isinstance(node, (defs.For, defs.Catch)):
			return self.__from_flow(node)
		else:
			return self.__resolve_procedural(node)

	def __from_reference(self, node: defs.Reference) -> SymbolRaw:
		"""シンボル参照ノードからシンボルを解決

		Args:
			node (Reference): 参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		if isinstance(node, defs.Var):
			return self.resolve(node)
		else:
			# defs.Relay
			return self.__resolve_procedural(node)

	def __from_flow(self, node: defs.For | defs.Catch) -> SymbolRaw:
		"""制御構文ノードからシンボルを解決

		Args:
			node (For | Catch): 制御構文ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		if isinstance(node, defs.For):
			return self.__resolve_procedural(node.for_in)
		else:
			# defs.Catch
			return self.resolve(node.var_type)

	def __resolve_procedural(self, node: Node) -> SymbolRaw:
		"""ノードを展開してシンボルを解決

		Args:
			node (Node): ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
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
			NotFoundError: シンボルが見つからない
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
		symbol_raw = self.__finder.find_by_symbolic(self.__raws, symbolic, prop_name)
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
			inherit_type_raw = self.__finder.by_symbolic(self.__raws, inherit_type)
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
		"""
		Note:
			# iterates
			## 無視できない
			* list: list<int>
			* dict: dict<str, int>
			* func_call: func<..., T> -> T = list<int> | dict<str, int>
			* variable: list<int> | dict<str, int>
			* relay: list<int> | dict<str, int>
			* indexer: list<int> | dict<str, int>
			## 無視してよい
			* group: Any
			* operator: Any
		"""
		def resolve() -> SymbolRaw:
			methods = {method.symbol.tokens: method for method in iterates.types.as_a(defs.Class).methods if method.symbol.tokens in ['__next__', '__iter__']}
			if '__next__' in methods:
				return self.symbols.resolve(methods['__next__'])
			else:
				return self.symbols.resolve(methods['__iter__'])

		def unpack(raw: SymbolRaw) -> list[defs.TemplateClass]:
			ts: list[defs.TemplateClass] = []
			if isinstance(raw.types, defs.TemplateClass):
				ts.append(raw.types)

			for in_raw in raw.attrs:
				ts.extend(unpack(in_raw))

			return ts

		def unpacked(raw: SymbolRaw, ts: list[defs.TemplateClass]) -> SymbolRaw:
			gs = [self.symbols.resolve(g_type).types for g_type in raw.types.generic_types]
			for index, g_type in enumerate(gs):
				if g_type in ts:
					return raw.attrs[index]

			raise LogicError('Unreachable code.')

		raw = resolve()
		ts = unpack(raw.attrs[-1])
		return unpacked(iterates, ts)

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
		return self.symbols.resolve(node)

	def on_decl_this_var(self, node: defs.DeclThisVar) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_decl_class_param(self, node: defs.DeclClassParam) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_decl_this_param(self, node: defs.DeclThisParam) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_types_name(self, node: defs.TypesName) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_import_name(self, node: defs.ImportName) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_relay(self, node: defs.Relay, receiver: SymbolRaw) -> SymbolRaw:
		# # receiver
		# variable.prop: a.b: A.T
		# variable.func_call: a.b(): A.b() -> T
		# relay.prop: a.b.c
		# relay.func_call: a.b.c()
		# func_call.prop: a.b().c
		# func_call.func_call: a.b().c()
		# indexer.prop: a.b[0].c()
		# indexer.func_call: a.b[1].c()
		return self.symbols.type_of_property(receiver.types, node.prop).to_ref(node, context=receiver)

	def on_class_ref(self, node: defs.ClassRef) -> SymbolRaw:
		return self.symbols.resolve(node).to_ref(node)

	def on_this_ref(self, node: defs.ThisRef) -> SymbolRaw:
		return self.symbols.resolve(node).to_ref(node)

	def on_argument_label(self, node: defs.ArgumentLabel) -> SymbolRaw:
		"""Note: labelに型はないのでUnknownを返す"""
		return self.symbols.type_of_primitive(classes.Unknown)

	def on_variable(self, node: defs.Var) -> SymbolRaw:
		return self.symbols.resolve(node).to_ref(node)

	def on_indexer(self, node: defs.Indexer, receiver: SymbolRaw, key: SymbolRaw) -> SymbolRaw:
		if receiver.types.is_a(defs.AltClass):
			receiver = receiver.attrs[0]

		if self.symbols.is_a(receiver, list):
			return receiver.attrs[0].to_ref(node, context=receiver)
		elif self.symbols.is_a(receiver, dict):
			return receiver.attrs[1].to_ref(node, context=receiver)
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
		"""
		Note:
			# calls
			* relay: a.b()
			* variable: a()
			* indexer: a[0]()
			* func_call: a()()
			# arguments
			* expression
		"""
		if isinstance(calls.types, defs.AltClass):
			calls = calls.attrs[0]

		if isinstance(calls.types, defs.Constructor):
			return self.symbols.resolve(calls.types.class_types.symbol)
		elif isinstance(calls.types, defs.Function):
			return FuncCallCompletion(self.symbols, node, calls, arguments).actual_return()
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
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

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
				# FIXME 必ずしも右オペランドの型が戻り値として正しいわけではない
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
		return self.symbols.type_of_primitive(classes.Pair).to_generic(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[SymbolRaw]) -> SymbolRaw:
		value_type = values[0] if len(values) > 0 else self.symbols.type_of_primitive(classes.Unknown)
		return self.symbols.type_of_primitive(list).to_generic(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[SymbolRaw]) -> SymbolRaw:
		if len(items) == 0:
			unknown_type = self.symbols.type_of_primitive(classes.Unknown)
			return self.symbols.type_of_primitive(dict).to_generic(node).extends(unknown_type, unknown_type)
		else:
			key_type, value_type = items[0].attrs
			return self.symbols.type_of_primitive(dict).to_generic(node).extends(key_type, value_type)

	# Expression

	def on_group(self, node: defs.Group, expression: SymbolRaw) -> SymbolRaw:
		return expression

	# Terminal

	def on_empty(self, node: defs.Empty) -> SymbolRaw:
		# XXX 厳密にいうとNullとEmptyは別だが、実用上はほぼ同じなので代用
		return self.symbols.type_of_primitive(None)


from typing import Callable, Generic, TypeAlias, cast

from py2cpp.node.node import T_Node


TemplateMap: TypeAlias = dict[str, defs.TemplateClass]
SymbolMap: TypeAlias = dict[str, SymbolRaw]
Callback: TypeAlias = Callable[[str], SymbolRaw]

class Completion(Generic[T_Node]):
	def __init__(self, symbols: Symbols, node: T_Node) -> None:
		self._symbols = symbols
		self._node = node

	def actual_return(self) -> SymbolRaw:
		raise NotImplementedError()

	def _unpack(self, raws: dict[str, SymbolRaw | list[SymbolRaw]]) -> dict[str, defs.TemplateClass]:
		expand_attrs = seqs.expand(raws, iter_key='attrs')
		return {path: attr.types for path, attr in expand_attrs.items() if isinstance(attr.types, defs.TemplateClass)}

	def _fetch_class_t_symbols(self, types: defs.ClassDef) -> list[SymbolRaw]:
		g_types = self._symbols.resolve(types).types.generic_types
		return [self._symbols.resolve(g_type) for g_type in g_types]

	def _make_updates(self, calls_ts: TemplateMap) -> dict[str, SymbolRaw]:
		primary, *sub_items = [DSN.elements(path)[0] for path in calls_ts.keys()]
		ts_primary = {path: t for path, t in calls_ts.items() if path.startswith(primary)}
		updates: SymbolMap = {}
		for key in sub_items:
			ts_sub_item = {path: t for path, t in calls_ts.items() if path.startswith(key)}
			updates = {**updates, **self.__actualized(key, ts_primary, ts_sub_item)}

		return updates

	def __actualized(self, key: str, ts_primary: TemplateMap, ts_sub_item: TemplateMap) -> SymbolMap:
		invoker = cast(Callback, getattr(self, f'actual_from_{key}'))
		updates: dict[str, SymbolRaw] = {}
		for path, t in ts_primary.items():
			founds = [in_path for in_path, t_arg in ts_sub_item.items() if t_arg == t]
			for found_path in founds:
				updates[path] = invoker(found_path)

		return updates

	def _apply_return(self, return_raw: SymbolRaw, updates: dict[str, SymbolRaw]) -> SymbolRaw:
		for path, attr in updates.items():
			seqs.update(return_raw.attrs, path, attr, iter_key='attrs')

		return return_raw


class FuncCallCompletion(Completion[defs.FuncCall]):
	def __init__(self, symbols: Symbols, node: defs.FuncCall, calls: SymbolRaw, arguments: list[SymbolRaw]) -> None:
		super().__init__(symbols, node)
		self.__calls = calls
		self.__arguments = arguments

	@property
	def class_t_symbols(self) -> list[SymbolRaw]:
		if not isinstance(self.__calls.types, (defs.Constructor, defs.ClassMethod, defs.Method)):
			return []
		
		return self._fetch_class_t_symbols(self.__calls.types.class_types)

	@property
	def args_symbols(self) -> list[SymbolRaw]:
		return self.__calls.attrs[:-1]

	@property
	def return_symbol(self) -> SymbolRaw:
		return self.__calls.attrs[-1]

	@implements
	def actual_return(self) -> SymbolRaw:
		unpacked = self._unpack({'return': self.return_symbol, 'args': self.args_symbols, 'class': self.class_t_symbols})
		if not len(unpacked):
			return self.return_symbol

		updates = self._make_updates(unpacked)
		if 'return' in updates:
			return updates['return']

		return self._apply_return(self.return_symbol, updates)

	def actual_from_args(self, found_path: str) -> SymbolRaw:
		index = int(DSN.elements(found_path)[1])
		return self.__arguments[index]

	def actual_from_class(self, found_path: str) -> SymbolRaw:
		index = int(DSN.elements(found_path)[1])
		return self.__calls.try_get_context().attrs[index]


class RelayCompletion(Completion[defs.Relay]):
	def __init__(self, symbols: Symbols, node: defs.Relay, receiver: SymbolRaw, prop: SymbolRaw) -> None:
		super().__init__(symbols, node)
		self.__receiver = receiver
		self.__prop = prop

	@property
	def receiver_symbol(self) -> SymbolRaw:
		return self.__receiver

	@property
	def prop_symbol(self) -> SymbolRaw:
		return self.__prop

	@property
	def class_t_symbols(self) -> list[SymbolRaw]:
		return self._fetch_class_t_symbols(self.__receiver.types)

	@implements
	def actual_return(self) -> SymbolRaw:
		unpacked = self._unpack({'receiver': self.receiver_symbol, 'prop': self.prop_symbol, 'class': self.class_t_symbols})
		if not len(unpacked):
			return self.receiver_symbol

		updates = self._make_updates(unpacked)
		if 'receiver' in updates:
			return updates['receiver']

		return self._apply_return(self.receiver_symbol, updates)

	def actual_from_prop(self, found_path: str) -> SymbolRaw:
		return self.__prop

	def actual_from_class(self, found_path: str) -> SymbolRaw:
		index = int(DSN.elements(found_path)[1])
		return self.__receiver.try_get_context().attrs[index]
