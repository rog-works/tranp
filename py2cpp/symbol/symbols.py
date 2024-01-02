from typing import Any, Callable, NamedTuple, TypeAlias

from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.annotation import injectable
import py2cpp.node.definition as defs
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node
from py2cpp.symbol.db import SymbolDB, SymbolRow

Symbolic: TypeAlias = defs.Symbol | defs.GenericType | defs.Literal | defs.ClassType
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

	def type_of(self, symbolic: Symbolic) -> SymbolSchema:
		"""シンボル系ノードからシンボルを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		found_row = self.__resolve_symbol(symbolic, self.__to_symbol_path(symbolic))
		if found_row is not None:
			return SymbolSchema(found_row)

		raise LogicError(f'Symbol not defined. node: {symbolic}')

	def property_of(self, class_type: defs.ClassType, symbol: defs.Symbol) -> SymbolSchema:
		"""クラスタイプノードからプロパティのシンボルを解決

		Args:
			class_type (ClassType): クラスタイプノード
			symbol (Symbol): プロパティのシンボルノード
		Returns:
			SymbolSchema: シンボルスキーマ
		Raises:
			LogicError: 未定義のシンボルを指定
		"""
		found_row = self.__resolve_symbol(class_type, self.__to_symbol_path(symbol))
		if found_row is not None:
			return SymbolSchema(found_row)

		raise LogicError(f'Symbol not defined. node: {class_type}')

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
			handler.on_action(node)

		# XXX 自分自身が含まれないため個別に実行
		handler.on_action(expression)

		return handler.result()

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
				return self.result_of(symbol_row.decl.as_a(defs.MoveAssign).value).row

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


class Handler:
	def __init__(self, resolver: Symbols) -> None:
		self.__resolver = resolver
		self.__stack: list[SymbolSchema] = []

	def result(self) -> SymbolSchema:
		if len(self.__stack) != 1:
			raise LogicError(f'Invalid number of stacks. {len(self.__stack)} != 1')

		return self.__stack.pop()

	def on_action(self, node: Node) -> None:
		if self.skiped(node):
			return

		self.__stack.append(self.invoke(node))

	def invoke(self, node: Node) -> SymbolSchema:
		handler_name = f'on_{node.classification}'
		handler = getattr(self, handler_name)
		args = self.invoke_args(node, handler)
		return handler(**args)

	def skiped(self, node: Node) -> bool:
		skip_types = (defs.Terminal,)
		return isinstance(node, *skip_types)

	def invoke_args(self, node: Node, handler: Callable) -> dict[str, Any]:
		def arg_is_list(anno: type) -> bool:
			return hasattr(anno, '__origin__') and getattr(anno, '__origin__') is list

		def pluck_arg(node: Node, anno: type, key: str) -> SymbolSchema | list[SymbolSchema]:
			if arg_is_list(anno):
				return pluck_arg_list(node, key)
			else:
				return self.__stack.pop()

		def pluck_arg_list(node: Node, key: str) -> list[SymbolSchema]:
			args = [self.__stack.pop() for _ in range(len(getattr(node, key)))]
			return list(reversed(args))

		def valid_arg(anno: type, arg: Node | SymbolSchema | list[SymbolSchema]) -> bool:
			if type(arg) is list:
				valids = [True for in_arg in arg if isinstance(in_arg, SymbolSchema)]
				return len(valids) == len(arg)
			else:
				return isinstance(arg, anno)

		keys = reversed([key for key, _ in handler.__annotations__.items() if key != 'return'])
		annos = {key: handler.__annotations__[key] for key in keys}
		node_key = list(annos.keys()).pop()
		args = {node_key: node, **{key: pluck_arg(node, annos[key], key) for key in annos.keys() if key != node_key}}
		valids = [True for key, arg in args.items() if valid_arg(annos[key], arg)]
		if len(valids) != len(args):
			raise LogicError(f'Invalid arguments. node: {node}, actual {len(valids)} to expected {len(args)}')

		return args

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: SymbolSchema, var_type: SymbolSchema, value: SymbolSchema) -> SymbolSchema:
		return var_type

	# Primary

	def on_symbol(self, node: defs.Symbol) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_symbol_relay(self, node: defs.SymbolRelay, receiver: SymbolSchema) -> SymbolSchema:
		return self.__resolver.property_of(receiver.row.types, node.property)

	def on_var(self, node: defs.Var) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_this(self, node: defs.This) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_this_var(self, node: defs.ThisVar) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_indexer(self, node: defs.Indexer, symbol: SymbolSchema, key: SymbolSchema) -> SymbolSchema:
		symbol_var_type = symbol.row.decl.as_a(defs.Parameter).var_type.as_a(defs.CollectionType)
		return self.__resolver.type_of(symbol_var_type.value_type)

	def on_list_type(self, node: defs.ListType, symbol: SymbolSchema, value_type: SymbolSchema) -> SymbolSchema:
		return symbol.extends(value_type=value_type.row)

	def on_dict_type(self, node: defs.DictType, symbol: SymbolSchema, key_type: SymbolSchema, value_type: SymbolSchema) -> SymbolSchema:
		return symbol.extends(key_type=key_type.row, value_type=value_type.row)

	def on_union_type(self, node: defs.UnionType) -> SymbolSchema:
		raise LogicError(f'Operation not supoorted. {node}')

	def on_func_call(self, node: defs.FuncCall, calls: SymbolSchema, arguments: list[SymbolSchema]) -> SymbolSchema:
		calls_function = calls.row.types.as_a(defs.Function)
		if calls_function.is_a(defs.Constructor):
			return self.__resolver.type_of(calls_function.as_a(defs.Constructor).class_symbol)
		else:
			return self.__resolver.type_of(calls_function.return_type.var_type)

	def on_super(self, node: defs.Super, calls: SymbolSchema, arguments: list[SymbolSchema]) -> SymbolSchema:
		return self.__resolver.type_of(node.class_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: SymbolSchema) -> SymbolSchema:
		return value

	# Operator

	def on_sum(self, node: defs.Sum, left: SymbolSchema, right: SymbolSchema) -> SymbolSchema:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.Sum, left: SymbolSchema, right: SymbolSchema, operator: str) -> SymbolSchema:
		methods = [method for method in left.row.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

		other = methods[0].parameters.pop()
		var_types = [other.var_type] if not other.var_type.is_a(defs.UnionType) else other.var_type.as_a(defs.UnionType).types
		for var_type in var_types:
			if self.__resolver.type_of(var_type.one_of(defs.Symbol | defs.GenericType)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_float(self, node: defs.Float) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_string(self, node: defs.String) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_truthy(self, node: defs.Truthy) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_falsy(self, node: defs.Falsy) -> SymbolSchema:
		return self.__resolver.type_of(node)

	def on_pair(self, node: defs.Pair, first: SymbolSchema, second: SymbolSchema) -> SymbolSchema:
		return self.__resolver.type_of(node).extends(first=first.row, second=second.row)

	def on_list(self, node: defs.List, values: list[SymbolSchema]) -> SymbolSchema:
		if len(values) == 0:
			return self.__resolver.type_of(node).extends(value=self.__resolver.unknown_of().row)
		else:
			return self.__resolver.type_of(node).extends(value=values[0].row)

	def on_dict(self, node: defs.Dict, items: list[PairSchema]) -> SymbolSchema:
		if len(items) == 0:
			return self.__resolver.type_of(node).extends(key=self.__resolver.unknown_of().row, value=self.__resolver.unknown_of().row)
		else:
			return self.__resolver.type_of(node).extends(key=items[0].first, value=items[0].second)
