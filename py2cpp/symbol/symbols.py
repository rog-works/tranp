from typing import TypeAlias

from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.annotation import injectable
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.symbol.db import SymbolDB, SymbolRow

Symbolic: TypeAlias = defs.Symbol | defs.GenericType | defs.Literal | defs.ClassType


class Symbols:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, db: SymbolDB) -> None:
		"""インスタンスを生成

		Args:
			db (SymbolDB): シンボルテーブル
		"""
		self.__db = db

	def type_of(self, symbolic: Symbolic) -> SymbolRow:
		"""シンボル系ノードからシンボルを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
		Returns:
			SymbolRow: シンボルデータ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		found_row = self.__resolve_symbol(symbolic, self.__to_symbol_path(symbolic))
		if found_row is not None:
			return found_row

		raise LogicError(f'Symbol not defined. node: {symbolic}')

	def property_of(self, class_type: defs.ClassType, symbol: defs.Symbol) -> SymbolRow:
		"""クラスタイプノードからプロパティのシンボルを解決

		Args:
			class_type (ClassType): クラスタイプノード
			symbol (Symbol): プロパティのシンボルノード
		Returns:
			SymbolRow: シンボルデータ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		found_row = self.__resolve_symbol(class_type, self.__to_symbol_path(symbol))
		if found_row is not None:
			return found_row

		raise LogicError(f'Symbol not defined. node: {class_type}')

	def __resolve_symbol(self, symbolic: Symbolic, symbol_path: str) -> SymbolRow | None:
		"""シンボルノードからタイプノードを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			symbol_path (str): シンボルパス
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		symbol_row = None

		# ドット区切りで前方からシンボルを検索
		elem_counts = DSN.length(symbol_path)
		remain_counts = elem_counts
		while remain_counts > 0:
			symbol_starts = DSN.left(symbol_path, elem_counts - (remain_counts - 1))
			found_row = self.__find_symbol(symbolic, symbol_starts)
			if found_row is None:
				break

			symbol_row = found_row
			remain_counts -= 1

		# シンボルが完全一致したデータを検出したら終了
		if symbol_row and remain_counts == 0:
			# XXX 宣言ノードによって型が明示されない場合は、右辺の代入式から型を補完する
			# XXX この処理にはいくつか問題がありそうなので、より良い方法があれば改善
			# XXX 1. type_ofとresule_ofが共依存している(循環参照)
			# XXX 2. MoveAssignだけが特別視され一貫性が無い
			# XXX 3. この処理を除外する手立てが無い(選択的でない)
			if symbol_row.decl.is_a(defs.MoveAssign):
				return self.result_of(symbol_row.decl.as_a(defs.MoveAssign).value)

			return symbol_row

		# 解決した部分を除外して探索シンボルを再編
		remain_path = DSN.right(symbol_path, remain_counts)

		# シンボルを検出、且つ検出したタイプがクラスノードの場合は再帰的に解決
		if symbol_row and symbol_row.types.is_a(defs.Class):
			return self.__resolve_symbol(symbol_row.types, remain_path)

		# シンボルが未検出、且つ対象ノードがクラスノードの場合は、クラスの継承チェーンを辿って解決
		if symbolic.is_a(defs.Class):
			return self.__resolve_symbol_from_class_chain(symbolic.as_a(defs.Class), remain_path)

		return None

	def __resolve_symbol_from_class_chain(self, class_type: defs.Class, symbol_path: str) -> SymbolRow | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			class_type (Class): クラスタイプノード
			symbol_path (str): シンボルパス
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		for symbol in class_type.parents:
			parent_type_row = self.__resolve_symbol(symbol, self.__to_symbol_path(symbol))
			if parent_type_row is None:
				break

			found_row = self.__resolve_symbol(parent_type_row.types, symbol_path)
			if found_row:
				return found_row

		return None

	def __to_symbol_path(self, symbolic: Symbolic) -> str:
		"""シンボルパスに変換

		Args:
			symbolic (Symbolic): シンボル系ノード
		Returns:
			str: シンボルパス
		"""
		if symbolic.is_a(defs.This, defs.ThisVar):
			return symbolic.tokens
		elif symbolic.is_a(defs.GenericType):
			return symbolic.as_a(defs.GenericType).symbol.tokens
		elif symbolic.is_a(defs.Literal):
			return symbolic.as_a(defs.Literal).class_symbol_alias
		elif symbolic.is_a(defs.ClassType):
			return symbolic.as_a(defs.ClassType).symbol.tokens
		else:
			# その他のSymbol
			return symbolic.tokens

	def __find_symbol(self, symbolic: Symbolic, symbol_path: str) -> SymbolRow | None:
		"""シンボルデータを検索。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			symbol_path (str): シンボルパス
		Returns:
			SymbolRow | None: シンボルデータ
		"""
		domain_id = DSN.join(symbolic.scope, symbol_path)
		domain_name = DSN.join(symbolic.module_path, symbol_path)
		if domain_id in self.__db.rows:
			return self.__db.rows[domain_id]
		elif domain_name in self.__db.rows:
			return self.__db.rows[domain_name]

		return None

	def result_of(self, expression: Node) -> SymbolRow:
		"""式ノードからシンボルを解決

		Args:
			expression (Node): 式ノード
		Returns:
			SymbolRow: シンボルデータ
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		handler = Handler(self)
		for node in expression.calculated():
			handler.on_action(node)

		# XXX 自分自身が含まれないため個別に実行
		handler.on_action(expression)

		return handler.result()


class Handler:
	def __init__(self, resolver: Symbols) -> None:
		self.__resolver = resolver
		self.__stack: list[SymbolRow] = []

	def result(self) -> SymbolRow:
		if len(self.__stack) != 1:
			raise LogicError(f'Invalid number of stacks. {len(self.__stack)} != 1')

		return self.__stack.pop()

	def on_action(self, node: Node) -> None:
		self.__stack.append(self.invoke(node))

	def invoke(self, node: Node) -> SymbolRow:
		handler_name = f'on_{node.classification}'
		handler = getattr(self, handler_name)
		keys = reversed([key for key, _ in handler.__annotations__.items() if key != 'return'])
		annos = {key: handler.__annotations__[key] for key in keys}
		node_key = list(annos.keys()).pop()
		args = {node_key: node, **{key: self.__stack.pop() for key in annos.keys() if key != node_key}}
		valids = [True for key, arg in args.items() if isinstance(arg, annos[key])]
		if len(valids) != len(args):
			raise LogicError(f'Invalid arguments. node: {node}, actual {len(valids)} to expected {len(args)}')

		return handler(**args)

	# Primary

	def on_symbol(self, node: defs.Symbol) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_symbol_relay(self, node: defs.SymbolRelay, receiver: SymbolRow) -> SymbolRow:
		return self.__resolver.property_of(receiver.types, node.property)

	def on_var(self, node: defs.Var) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_this(self, node: defs.This) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_this_var(self, node: defs.ThisVar) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_indexer(self, node: defs.Indexer, symbol: SymbolRow, key: SymbolRow) -> SymbolRow:
		symbol_var_type = symbol.decl.as_a(defs.Parameter).var_type.as_a(defs.CollectionType)
		return self.__resolver.type_of(symbol_var_type.value_type)

	def on_list_type(self, node: defs.ListType) -> SymbolRow:
		return self.on_generic_type(node)

	def on_dict_type(self, node: defs.DictType) -> SymbolRow:
		return self.on_generic_type(node)

	def on_union_type(self, node: defs.UnionType) -> SymbolRow:
		raise LogicError(f'Operation not supoorted. {node}')

	def on_generic_type(self, node: defs.GenericType) -> SymbolRow:
		return self.__resolver.type_of(node.symbol)

	def on_func_call(self, node: defs.FuncCall, calls: SymbolRow, arguments: list[SymbolRow]) -> SymbolRow:
		calls_function = calls.types.as_a(defs.Function)
		if calls_function.is_a(defs.Constructor):
			return self.__resolver.type_of(calls_function.as_a(defs.Constructor).class_symbol)
		else:
			return self.__resolver.type_of(calls_function.return_type.var_type)

	def on_super(self, node: defs.Super, calls: SymbolRow, arguments: list[SymbolRow]) -> SymbolRow:
		return self.__resolver.type_of(node.class_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: SymbolRow) -> SymbolRow:
		return value

	# Operator

	def on_sum(self, node: defs.Sum, left: SymbolRow, right: SymbolRow) -> SymbolRow:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.Sum, left: SymbolRow, right: SymbolRow, operator: str) -> SymbolRow:
		methods = [method for method in left.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left.types}, {right.types}, {operator}')

		other = methods[0].parameters.pop()
		var_types = [other.var_type] if not other.var_type.is_a(defs.UnionType) else other.var_type.as_a(defs.UnionType).types
		for var_type in var_types:
			if self.__resolver.type_of(var_type.one_of(defs.Symbol | defs.GenericType)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left.types}, {right.types}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_float(self, node: defs.Float) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_string(self, node: defs.String) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_truthy(self, node: defs.Truthy) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_falsy(self, node: defs.Falsy) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_list(self, node: defs.List) -> SymbolRow:
		return self.__resolver.type_of(node)

	def on_dict(self, node: defs.Dict) -> SymbolRow:
		return self.__resolver.type_of(node)
