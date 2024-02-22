from types import UnionType
from typing import Callable

from rogw.tranp.analyze.db import SymbolDB
from rogw.tranp.analyze.symbol import SymbolRaw
from rogw.tranp.analyze.procedure import Procedure
import rogw.tranp.analyze.reflection as reflection
from rogw.tranp.analyze.finder import SymbolFinder
import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.compatible.python.types import Primitives
from rogw.tranp.errors import LogicError, NotFoundError
from rogw.tranp.lang.implementation import injectable
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node


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
		self.__handlers: dict[str, list[Callable[..., SymbolRaw]]] = {}

	def is_a(self, symbol: SymbolRaw, primitive_type: type[Primitives] | None) -> bool:
		"""シンボルの型を判定

		Args:
			symbol (SymbolRaw): シンボル
			primitive_type (type[Primitives] | None): プリミティブ型
		Return:
			bool: True = 指定の型と一致
		"""
		return symbol.types == self.type_of_primitive(primitive_type).types

	def get_object(self) -> SymbolRaw:
		"""objectのシンボルを取得

		Returns:
			SymbolRaw: シンボル
		Raises:
			LogicError: objectが未実装
		"""
		return self.__finder.get_object(self.__raws)

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

	def type_of_property(self, types: defs.ClassDef, prop: defs.Var) -> SymbolRaw:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			types (ClassDef): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		return self.resolve(types, prop.tokens)

	def type_of_constructor(self, types: defs.Class) -> SymbolRaw:
		"""クラス定義ノードからコンストラクターのシンボルを解決

		Args:
			class (Class): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		Note:
			FIXME Pythonのコンストラクターに依存したコードはNG。再度検討
		"""
		return self.resolve(types, '__init__')

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
			return self.__resolve_procedural(node)
		elif isinstance(node, defs.ClassDef):
			return self.resolve(node)
		elif isinstance(node, defs.Literal):
			return self.__resolve_procedural(node)
		elif isinstance(node, (defs.For, defs.Catch)):
			return self.__from_flow(node)
		elif isinstance(node, (defs.Comprehension, defs.CompFor)):
			return self.__from_comprehension(node)
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

	def __from_comprehension(self, node: defs.Comprehension | defs.CompFor) -> SymbolRaw:
		"""リスト内包表記関連ノードからシンボルを解決

		Args:
			node (Comprehension | CompFor): リスト内包表記関連ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		if isinstance(node, defs.Comprehension):
			projection_type = list if node.is_a(defs.ListComp) else dict
			origin = self.type_of_primitive(projection_type)
			projection = self.__resolve_procedural(node.projection)
			# XXX 属性の扱いの違いを吸収
			# XXX list: int
			# XXX dict: Pair<str, int>
			attrs = [projection] if projection_type is list else projection.attrs
			return origin.to.literal(node).extends(*attrs)
		else:
			# CompFor
			return self.__resolve_procedural(node.for_in)

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

		raise NotFoundError(f'SymbolRaw not defined. symbolic: {symbolic.fullyname}, prop_name: {prop_name}')

	def __resolve_raw(self, symbolic: defs.Symbolic, prop_name: str) -> SymbolRaw | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		symbol_raw = self.__finder.find_by_symbolic(self.__raws, symbolic, prop_name)
		if symbol_raw is None and isinstance(symbolic, defs.Class):
			symbol_raw = self.__resolve_raw_recursive(symbolic, prop_name)

		return symbol_raw

	def __resolve_raw_recursive(self, types: defs.Class, prop_name: str) -> SymbolRaw | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			types (Class): クラス定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			SymbolRaw | None: シンボルデータ
		"""
		for inherit_type in types.inherits:
			inherit_type_raw = self.__finder.by_symbolic(self.__raws, inherit_type)
			found_raw = self.__resolve_raw(inherit_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		# 全てのクラスはobjectを継承している前提のため、暗黙的にフォールバック
		super_type = self.get_object()
		if super_type.types != types:
			found_raw = self.__resolve_raw(super_type.types, prop_name)
			if found_raw:
				return found_raw

		return None

	def on(self, action: str, handler: Callable[..., SymbolRaw]) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): アクション名
			handler (Callable[..., T_Ret]): ハンドラー
		"""
		if action not in self.__handlers:
			self.__handlers[action] = []

		if handler not in self.__handlers[action]:
			self.__handlers[action].append(handler)

	def off(self, action: str, handler: Callable[..., SymbolRaw]) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): アクション名
			handler (Callable[..., T_Ret]): ハンドラー
		"""
		if action in self.__handlers:
			self.__handlers[action].remove(handler)

	def __resolve_procedural(self, node: Node) -> SymbolRaw:
		"""ノードを展開してシンボルを解決

		Args:
			node (Node): ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			NotFoundError: シンボルが見つからない
		"""
		procedure = ProceduralResolver(self)
		for key, handlers in self.__handlers.items():
			for handler in handlers:
				procedure.on(key, handler)

		return procedure.resolve(node)


class ProceduralResolver:
	"""プロシージャルリゾルバー。ASTを再帰的に解析してシンボルを解決"""

	def __init__(self, symbols: Symbols) -> None:
		"""インスタンスを生成

		Args:
			symbols (Symbols): シンボルリゾルバー
		"""
		self.symbols = symbols
		self.__procedure = self.__make_procedure()

	def __make_procedure(self) -> Procedure[SymbolRaw]:
		"""プロシージャーを生成

		Returns:
			Procedure[SymbolRaw]: プロシージャー
		"""
		handlers = {key: getattr(self, key) for key in ProceduralResolver.__dict__.keys() if key.startswith('on_')}
		procedure = Procedure[SymbolRaw](verbose=False)
		for key, handler in handlers.items():
			procedure.on(key, handler)

		return procedure

	def on(self, action: str, handler: Callable[..., SymbolRaw]) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): アクション名
			handler (Callable[..., T_Ret]): ハンドラー
		"""
		self.__procedure.on(action, handler)

	def resolve(self, node: Node) -> SymbolRaw:
		"""指定のノードからASTを再帰的に解析し、シンボルを解決

		Args:
			node (Node): ノード
		Returns:
			SymbolRaw: シンボル
		"""
		return self.__procedure.exec(node)

	# Fallback

	def on_fallback(self, node: Node) -> SymbolRaw:
		"""
		Note:
			シンボルとして解釈出来ないノードが対象。一律Unknownとして返却
			# 対象
			* Terminal(Operator)
		"""
		return self.symbols.type_of_primitive(classes.Unknown)

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
		if isinstance(iterates.types, defs.AltClass):
			iterates = iterates.attrs[0]

		def resolve() -> SymbolRaw:
			# FIXME __class_getitem__と同様にクラスチェーンを考慮する必要あり
			methods = {method.symbol.tokens: method for method in iterates.types.as_a(defs.Class).methods if method.symbol.tokens in ['__next__', '__iter__']}
			if '__next__' in methods:
				return self.symbols.resolve(methods['__next__'])
			else:
				return self.symbols.resolve(methods['__iter__'])

		method = resolve()
		schema = {
			'klass': method.attrs[0],
			'parameters': method.attrs[1:-1],
			# XXX iter関数の動作再現として、__iter__の場合のみ戻り値内のT_Seqをアンパックする(期待値: `__iter__(self) -> Iterator[T_Seq]`)
			'returns': method.attrs[-1] if method.types.domain_name == '__next__' else method.attrs[-1].attrs[0],
		}
		method_ref = reflection.Builder(method).schema(lambda: schema).build(reflection.Method)
		return method_ref.returns(iterates)

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: SymbolRaw, var_type: SymbolRaw, default_value: SymbolRaw) -> SymbolRaw:
		return symbol

	# Statement simple

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: SymbolRaw, var_type: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return receiver

	def on_move_assign(self, node: defs.MoveAssign, receivers: list[SymbolRaw], value: SymbolRaw) -> SymbolRaw:
		return value

	def on_aug_assign(self, node: defs.AugAssign, receiver: SymbolRaw, operator: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return receiver

	def on_return(self, node: defs.Return, return_value: SymbolRaw) -> SymbolRaw:
		return return_value

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
		if isinstance(receiver.types, defs.AltClass):
			receiver = receiver.attrs[0]

		# クラス属性へのアクセスの場合は__class_getitem__経由で型を解決
		# FIXME on_superによって解決されたreceiverは、インスタンス属性へのアクセスと見做して除外する ※アクセス対象がクラスかインスタンスか区別出来ないため
		if not node.receiver.is_a(defs.Super) and isinstance(receiver.decl, defs.Class):
			try:
				getitem = self.symbols.resolve(receiver.decl, '__class_getitem__')
				# XXX clsにタイプヒントが付与された場合、returnsの第1引数のreceiverと階層を合わせるためアンパックする ※タイプヒントが無い場合は必然的に階層が同じになる
				# XXX (例: '__class_getitem__(cls: type[T], *: Any) -> Any')
				class_type = getitem.attrs[0].attrs[0] if len(getitem.attrs[0].attrs) > 0 else getitem.attrs[0]
				getitem_ref = reflection.Builder(getitem) \
					.schema(lambda: {'klass': class_type, 'parameters': getitem.attrs[1:-2], 'returns': getitem.attrs[-1]}) \
					.build(reflection.ClassMethod)
				return getitem_ref.returns(receiver, *getitem.attrs[1:-2])
			except NotFoundError:
				pass

		return self.symbols.type_of_property(receiver.types, node.prop).to.ref(node, context=receiver)

	def on_class_ref(self, node: defs.ClassRef) -> SymbolRaw:
		return self.symbols.resolve(node).to.ref(node)

	def on_this_ref(self, node: defs.ThisRef) -> SymbolRaw:
		return self.symbols.resolve(node).to.ref(node)

	def on_argument_label(self, node: defs.ArgumentLabel) -> SymbolRaw:
		"""Note: labelに型はないのでUnknownを返す"""
		return self.symbols.type_of_primitive(classes.Unknown)

	def on_variable(self, node: defs.Var) -> SymbolRaw:
		return self.symbols.resolve(node).to.ref(node)

	def on_indexer(self, node: defs.Indexer, receiver: SymbolRaw, key: SymbolRaw) -> SymbolRaw:
		if receiver.types.is_a(defs.AltClass):
			receiver = receiver.attrs[0]

		if self.symbols.is_a(receiver, list):
			return receiver.attrs[0].to.ref(node, context=receiver)
		elif self.symbols.is_a(receiver, dict):
			return receiver.attrs[1].to.ref(node, context=receiver)
		else:
			# XXX コレクション型以外は全て通常のクラスである想定
			# XXX keyに何が入るべきか特定できないためreceiverをそのまま返却
			# XXX この状況で何が取得されるべきかは利用側で判断することとする
			return receiver.to.ref(node, context=receiver)

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: SymbolRaw) -> SymbolRaw:
		"""Note: XXX Pythonではtypeをアンパックする構文が存在しないためAltClassも同様に扱う"""
		return self.symbols.type_of_property(receiver.types, node.prop)

	def on_var_of_type(self, node: defs.VarOfType) -> SymbolRaw:
		return self.symbols.resolve(node)

	def on_list_type(self, node: defs.ListType, type_name: SymbolRaw, value_type: SymbolRaw) -> SymbolRaw:
		return type_name.to.generic(node).extends(value_type)

	def on_dict_type(self, node: defs.DictType, type_name: SymbolRaw, key_type: SymbolRaw, value_type: SymbolRaw) -> SymbolRaw:
		return type_name.to.generic(node).extends(key_type, value_type)

	def on_custom_type(self, node: defs.CustomType, type_name: SymbolRaw, template_types: list[SymbolRaw]) -> SymbolRaw:
		return type_name.to.generic(node).extends(*template_types)

	def on_union_type(self, node: defs.UnionType, or_types: list[SymbolRaw]) -> SymbolRaw:
		return self.symbols.type_of_primitive(UnionType).to.generic(node).extends(*or_types)

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
		actual_calls = calls
		if isinstance(calls.types, defs.AltClass):
			actual_calls = calls.attrs[0]

		if isinstance(actual_calls.types, defs.Class):
			# XXX クラス経由で暗黙的にコンストラクターを呼び出した場合
			# XXX 戻り値の型をクラスのシンボルで補完
			# XXX この際のクラスのシンボルはSymbolReferenceになり、そのままだと属性の設定が出来ないため、SymbolVarに変換する
			constroctur_calls = self.symbols.type_of_constructor(actual_calls.types)
			func = reflection.Builder(constroctur_calls) \
				.schema(lambda: {'parameters': constroctur_calls.attrs[1:-1], 'returns': actual_calls.to.var(actual_calls.decl)}) \
				.build(reflection.Constructor)
			return func.returns(*arguments)
		elif isinstance(actual_calls.types, defs.Constructor):
			# XXX コンストラクターを明示的に呼び出した場合
			# XXX 戻り値の型を第1引数(自己参照)で補完
			func = reflection.Builder(actual_calls) \
				.schema(lambda: {'parameters': actual_calls.attrs[1:-1], 'returns': actual_calls.attrs[0]}) \
				.build(reflection.Constructor)
			return func.returns(*arguments)
		else:
			func = reflection.Builder(actual_calls) \
				.case(reflection.Method).schema(lambda: {'klass': actual_calls.attrs[0], 'parameters': actual_calls.attrs[1:-1], 'returns': actual_calls.attrs[-1]}) \
				.other_case().schema(lambda: {'parameters': actual_calls.attrs[:-1], 'returns': actual_calls.attrs[-1]}) \
				.build(reflection.Function)
			if func.is_a(reflection.Method):
				return func.returns(actual_calls.context, *arguments)
			else:
				return func.returns(*arguments)

	def on_super(self, node: defs.Super, calls: SymbolRaw, arguments: list[SymbolRaw]) -> SymbolRaw:
		return self.symbols.resolve(node.super_class_symbol)

	def on_argument(self, node: defs.Argument, label: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: SymbolRaw) -> SymbolRaw:
		return class_type

	def on_comp_for(self, node: defs.CompFor, symbols: list[SymbolRaw], for_in: SymbolRaw) -> SymbolRaw:
		return for_in

	def on_list_comp(self, node: defs.ListComp, projection: SymbolRaw, fors: list[SymbolRaw], condition: SymbolRaw) -> SymbolRaw:
		return projection

	def on_dict_comp(self, node: defs.ListComp, projection: SymbolRaw, fors: list[SymbolRaw], condition: SymbolRaw) -> SymbolRaw:
		return projection

	# Operator

	def on_factor(self, node: defs.Sum, operator: SymbolRaw, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_not_compare(self, node: defs.NotCompare, value: SymbolRaw) -> SymbolRaw:
		return value

	def on_or_compare(self, node: defs.OrCompare, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_and_compare(self, node: defs.AndCompare, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_comparison(self, node: defs.Comparison, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
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

	def on_or_bitwise(self, node: defs.OrBitwise, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__or__')

	def on_xor_bitwise(self, node: defs.XorBitwise, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__xor__')

	def on_and_bitwise(self, node: defs.AndBitwise, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		return self.each_binary_operator(node, left, right, '__and__')

	def on_shift_bitwise(self, node: defs.Sum, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'<<': '__lshift__',
			'>>': '__rshift__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_sum(self, node: defs.Sum, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'+': '__add__',
			'-': '__sub__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def on_term(self, node: defs.Term, left: SymbolRaw, operator: SymbolRaw, right: list[SymbolRaw]) -> SymbolRaw:
		operators = {
			'*': '__mul__',
			'/': '__truediv__',
			'%': '__mod__',
		}
		return self.each_binary_operator(node, left, right, operators[node.operator.tokens])

	def each_binary_operator(self, node: defs.BinaryOperator, left: SymbolRaw, right: list[SymbolRaw], operator: str) -> SymbolRaw:
		symbol = self.proc_binary_operator(node, left, right[0], operator)
		for in_right in right[1:]:
			symbol = self.proc_binary_operator(node, symbol, in_right, operator)

		return symbol

	def proc_binary_operator(self, node: defs.BinaryOperator, left: SymbolRaw, right: SymbolRaw, operator: str) -> SymbolRaw:
		# FIXME __class_getitem__と同様にクラスチェーンを考慮する必要あり
		in_left = [method for method in left.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		in_right = [method for method in right.types.as_a(defs.Class).methods if method.symbol.tokens == operator]
		methods = [*in_left, *in_right]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {str(left)} {operator} {str(right)}')

		for method in methods:
			with_left = method in in_left
			other = method.parameters[-1]
			var_types = other.var_type.or_types if isinstance(other.var_type, defs.UnionType) else [other.var_type]
			for var_type in var_types:
				type_raw = self.symbols.resolve(var_type.as_a(defs.Type))
				if (with_left and type_raw == right) or (not with_left and type_raw == left):
					return self.symbols.resolve(method.return_type)

		raise LogicError(f'Operation not allowed. {node}, {str(left)} {operator} {str(right)}')

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
		return self.symbols.type_of_primitive(classes.Pair).to.literal(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[SymbolRaw]) -> SymbolRaw:
		value_type = values[0] if len(values) > 0 else self.symbols.type_of_primitive(classes.Unknown)
		return self.symbols.type_of_primitive(list).to.literal(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[SymbolRaw]) -> SymbolRaw:
		if len(items) == 0:
			unknown_type = self.symbols.type_of_primitive(classes.Unknown)
			return self.symbols.type_of_primitive(dict).to.literal(node).extends(unknown_type, unknown_type)
		else:
			key_type, value_type = items[0].attrs
			return self.symbols.type_of_primitive(dict).to.literal(node).extends(key_type, value_type)

	def on_null(self, node: defs.Null) -> SymbolRaw:
		return self.symbols.type_of_primitive(None)

	# Expression

	def on_group(self, node: defs.Group, expression: SymbolRaw) -> SymbolRaw:
		return expression

	# Terminal

	def on_empty(self, node: defs.Empty) -> SymbolRaw:
		# XXX 厳密にいうとNullとEmptyは別だが、実用上はほぼ同じなので代用
		return self.symbols.type_of_primitive(None)
