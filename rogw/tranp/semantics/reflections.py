from rogw.tranp.semantics.reflection.db import SymbolDBProvider
import rogw.tranp.semantics.reflection.helper.template as template
import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.error import raises
from rogw.tranp.semantics.errors import OperationNotAllowedError, SemanticsLogicError, UnresolvedSymbolError
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.procedure import Procedure
from rogw.tranp.semantics.reflection.interface import IReflection
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class Reflections:
	"""シンボルテーブルを参照してシンボルの型を解決する機能を提供"""

	@injectable
	def __init__(self, db_provider: SymbolDBProvider, finder: SymbolFinder, plugins: PluginProvider) -> None:
		"""インスタンスを生成

		Args:
			db_provider (SymbolDBProvider): シンボルテーブルプロバイダー @inject
			finder (SymbolFinder): シンボル検索 @inject
			plugins (PluginProvider): プラグインプロバイダー @inject
		"""
		self.__db = db_provider.db
		self.__finder = finder
		self.__plugins = plugins
		self.__procedural: ProceduralResolver | None = None

	@property
	def __procedural_resolver(self) -> 'ProceduralResolver':
		"""ProceduralResolver: プロシージャルリゾルバー"""
		if self.__procedural is None:
			self.__procedural = ProceduralResolver(self)

			for plugin in self.__plugins():
				plugin.register(self.__procedural.procedure)

		return self.__procedural

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def is_a(self, symbol: IReflection, standard_type: type[Standards] | None) -> bool:
		"""シンボルの型を判定

		Args:
			symbol (IReflection): シンボル
			standard_type (type[Standards] | None): 標準クラス
		Return:
			bool: True = 指定の型と一致
		Raises:
			UnresolvedSymbolError: 標準クラスが未実装
		"""
		return symbol.types == self.type_of_standard(standard_type).types

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def get_object(self) -> IReflection:
		"""objectのシンボルを取得

		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: objectが未実装
		"""
		return self.__finder.get_object(self.__db)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def from_fullyname(self, fullyname: str) -> IReflection:
		"""完全参照名からシンボルを解決

		Args:
			fullyname (str): 完全参照名
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: シンボルの解決に失敗
		"""
		return self.__finder.by(self.__db, fullyname)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def type_of_standard(self, standard_type: type[Standards] | None) -> IReflection:
		"""標準クラスのシンボルを解決

		Args:
			standard_type (type[Standard] | None): 標準クラス
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: 標準クラスが未実装
		"""
		return self.__finder.by_standard(self.__db, standard_type)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def type_of_property(self, types: defs.ClassDef, prop: defs.Var) -> IReflection:
		"""クラス定義ノードと変数参照ノードからプロパティーのシンボルを解決

		Args:
			types (ClassDef): クラス定義ノード
			prop (Var): 変数参照ノード
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: シンボルの解決に失敗
		"""
		return self.resolve(types, prop.tokens)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def type_of_constructor(self, types: defs.Class) -> IReflection:
		"""クラス定義ノードからコンストラクターのシンボルを解決

		Args:
			types (Class): クラス定義ノード
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: コンストラクターの実装ミス
		"""
		return self.resolve(types, types.operations.constructor)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def type_of(self, node: Node) -> IReflection:
		"""シンボル系/式ノードからシンボルを解決 XXX 万能過ぎるので細分化を検討

		Args:
			node (Node): シンボル系/式ノード
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.Declable):
			return self.__from_declable(node)
		elif isinstance(node, defs.Reference):
			return self.__resolve_procedural(node)
		elif isinstance(node, defs.Type):
			return self.__resolve_procedural(node)
		elif isinstance(node, defs.ClassDef):
			return self.__from_class_def(node)
		elif isinstance(node, defs.Literal):
			return self.__resolve_procedural(node)
		elif isinstance(node, (defs.For, defs.Catch, defs.WithEntry)):
			return self.__from_flow(node)
		elif isinstance(node, (defs.Comprehension, defs.CompFor)):
			return self.__from_comprehension(node)
		else:
			return self.__resolve_procedural(node)

	def __from_declable(self, node: defs.Declable) -> IReflection:
		"""シンボル宣言ノードからシンボルを解決

		Args:
			node (ClassDef): シンボル宣言ノード
		Returns:
			IReflection: シンボル
		Raises:
			SemanticsError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.DeclClassParam) and isinstance(node.declare.as_a(defs.Parameter).var_type, defs.Empty):
			return self.type_of_standard(type).stack(node).extends(self.resolve(node))
		elif isinstance(node, defs.TypesName) and isinstance(node.parent, defs.Class):
			return self.type_of_standard(type).stack(node).extends(self.resolve(node))
		else:
			return self.resolve(node).stack(node)

	def __from_class_def(self, node: defs.ClassDef) -> IReflection:
		"""クラス定義ノードからシンボルを解決

		Args:
			node (ClassDef): クラス定義ノード
		Returns:
			IReflection: シンボル
		Raises:
			SemanticsError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.Class):
			return self.type_of_standard(type).stack(node).extends(self.resolve(node))
		else:
			# defs.Function
			return self.resolve(node).stack(node)

	def __from_flow(self, node: defs.For | defs.Catch | defs.WithEntry) -> IReflection:
		"""制御構文ノードからシンボルを解決

		Args:
			node (For | Catch | WithEntry): 制御構文ノード
		Returns:
			IReflection: シンボル
		Raises:
			SemanticsError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.For):
			return self.__resolve_procedural(node.for_in)
		elif isinstance(node, defs.WithEntry):
			return self.__resolve_procedural(node.enter)
		else:
			# defs.Catch
			return self.resolve(node.var_type).stack(node)

	def __from_comprehension(self, node: defs.Comprehension | defs.CompFor) -> IReflection:
		"""リスト内包表記関連ノードからシンボルを解決

		Args:
			node (Comprehension | CompFor): リスト内包表記関連ノード
		Returns:
			IReflection: シンボル
		Raises:
			SemanticsError: シンボルの解決に失敗
		"""
		if isinstance(node, defs.Comprehension):
			return self.__resolve_procedural(node)
		else:
			# CompFor
			return self.__resolve_procedural(node.for_in)

	@raises(UnresolvedSymbolError, SemanticsLogicError)
	def resolve(self, symbolic: defs.Symbolic, prop_name: str = '') -> IReflection:
		"""シンボルテーブルからシンボルを解決

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			IReflection: シンボル
		Raises:
			UnresolvedSymbolError: シンボルの解決に失敗
		"""
		found_raw = self.__resolve_raw(symbolic, prop_name)
		if found_raw is not None:
			return found_raw

		raise UnresolvedSymbolError(f'symbolic: {symbolic.fullyname}, prop_name: {prop_name}')

	def __resolve_raw(self, symbolic: defs.Symbolic, prop_name: str) -> IReflection | None:
		"""シンボル系ノードからシンボルを解決。未検出の場合はNoneを返却

		Args:
			symbolic (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			IReflection | None: シンボルデータ
		"""
		symbol_raw = self.__finder.find_by_symbolic(self.__db, symbolic, prop_name)
		if symbol_raw is None and isinstance(symbolic, defs.Class):
			symbol_raw = self.__resolve_raw_recursive(symbolic, prop_name)
		elif symbol_raw is None and isinstance(symbolic, defs.Function):  # XXX 関数もオブジェクトなので誤りではないが検討の余地あり
			symbol_raw = self.__resolve_raw_fallback(symbolic, prop_name)

		return symbol_raw

	def __resolve_raw_recursive(self, types: defs.Class, prop_name: str) -> IReflection | None:
		"""クラスの継承チェーンを辿ってシンボルを解決。未検出の場合はNoneを返却

		Args:
			types (Class): クラス定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			IReflection | None: シンボルデータ
		"""
		for inherit_type in types.inherits:
			inherit_type_raw = self.__finder.by_symbolic(self.__db, inherit_type)
			found_raw = self.__resolve_raw(inherit_type_raw.types, prop_name)
			if found_raw:
				return found_raw

		return self.__resolve_raw_fallback(types, prop_name)

	def __resolve_raw_fallback(self, types: defs.Class | defs.Function, prop_name: str) -> IReflection | None:
		"""再帰探査の最後にobjectからシンボルを解決。未検出の場合はNoneを返却

		Args:
			types (Class | Function): クラス・関数定義ノード
			prop_name (str): プロパティー名(空文字の場合は無視される)
		Returns:
			IReflection | None: シンボルデータ
		"""
		super_type = self.get_object()
		if super_type.types != types:
			found_raw = self.__resolve_raw(super_type.types, prop_name)
			if found_raw:
				return found_raw

		return None

	def __resolve_procedural(self, node: Node) -> IReflection:
		"""ノードを展開してシンボルを解決

		Args:
			node (Node): ノード
		Returns:
			IReflection: シンボル
		Raises:
			ProcessingError: シンボルの解決に失敗
		"""
		return self.__procedural_resolver.resolve(node)


class ProceduralResolver:
	"""プロシージャルリゾルバー。ASTを再帰的に解析してシンボルを解決"""

	def __init__(self, reflections: Reflections) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー
		"""
		self.reflections = reflections
		self.procedure = self.__make_procedure()

	def __make_procedure(self) -> Procedure[IReflection]:
		"""プロシージャーを生成

		Returns:
			Procedure[IReflection]: プロシージャー
		"""
		handlers = {key: getattr(self, key) for key in ProceduralResolver.__dict__.keys() if key.startswith('on_')}
		procedure = Procedure[IReflection](verbose=False)
		for key, handler in handlers.items():
			procedure.on(key, handler)

		return procedure

	def resolve(self, node: Node) -> IReflection:
		"""指定のノードからASTを再帰的に解析し、シンボルを解決

		Args:
			node (Node): ノード
		Returns:
			IReflection: シンボル
		Raises:
			ProcessingError: 実行エラー
		"""
		return self.procedure.exec(node)

	def force_unpack_nullable(self, symbol: IReflection) -> IReflection:
		"""Nullableのシンボルの変数の型をアンパック。Nullable以外の型はそのまま返却 (主にRelayで利用)

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: 変数の型
		Note:
			許容するNullableの書式 (例: 'Class | None')
		"""
		if self.reflections.is_a(symbol, classes.Union) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.is_a(symbol.attrs[0], None)
			is_1_null = self.reflections.is_a(symbol.attrs[1], None)
			if is_0_null != is_1_null:
				return symbol.attrs[1 if is_0_null else 0]

		return symbol

	def unpack_alt_class(self, symbol: IReflection) -> IReflection:
		"""AltClass型をアンパック

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: 変数の型
		"""
		return symbol.attrs[0] if isinstance(symbol.types, defs.AltClass) else symbol

	def unpack_type_proxy(self, symbol: IReflection) -> IReflection:
		"""typeのProxy型をアンパック

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: 変数の型
		Note:
			対象: type<T> -> T
		"""
		return symbol.attrs[0] if isinstance(symbol.decl, defs.Class) and self.reflections.is_a(symbol, type) else symbol

	# Fallback

	def on_fallback(self, node: Node) -> IReflection:
		"""
		Note:
			シンボルとして解釈出来ないノードが対象。一律Unknownとして返却
			# 対象
			* Terminal(Operator)
		"""
		return self.reflections.type_of_standard(classes.Unknown).stack(node)

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: IReflection, var_type: IReflection, default_value: IReflection) -> IReflection:
		return symbol.stack(node)

	# Statement simple

	def on_move_assign(self, node: defs.MoveAssign, receivers: list[IReflection], value: IReflection) -> IReflection:
		return value.stack(node)

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: IReflection, var_type: IReflection, value: IReflection) -> IReflection:
		return receiver.stack(node)

	def on_aug_assign(self, node: defs.AugAssign, receiver: IReflection, value: IReflection) -> IReflection:
		return receiver.stack(node)

	def on_return(self, node: defs.Return, return_value: IReflection) -> IReflection:
		return return_value.stack(node)

	def on_yield(self, node: defs.Yield, yield_value: IReflection) -> IReflection:
		"""Note: XXX Iteratorで囲うべきか検討。値としてだけみればこのままでも良い"""
		return yield_value.stack(node)

	# Primary

	def on_argument(self, node: defs.Argument, label: IReflection, value: IReflection) -> IReflection:
		return value.stack(node)

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: IReflection) -> IReflection:
		return class_type.stack(node)

	def on_argument_label(self, node: defs.ArgumentLabel) -> IReflection:
		"""Note: labelに型はないのでUnknownを返却"""
		return self.reflections.type_of_standard(classes.Unknown).stack(node)

	def on_decl_class_var(self, node: defs.DeclClassVar) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_decl_this_var_forward(self, node: defs.DeclThisVarForward) -> IReflection:
		"""Note: XXX 型を評価する必要がないのでUnknownを返却"""
		return self.reflections.type_of_standard(classes.Unknown).stack(node)

	def on_decl_this_var(self, node: defs.DeclThisVar) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_decl_class_param(self, node: defs.DeclClassParam) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_decl_this_param(self, node: defs.DeclThisParam) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_types_name(self, node: defs.TypesName) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_import_name(self, node: defs.ImportName) -> IReflection:
		"""Note: @deprecated XXX ImportAsName内で利用されるだけでこのノードは展開されないためハンドラーは不要"""
		return self.reflections.resolve(node).stack(node)

	def on_import_as_name(self, node: defs.ImportAsName) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_relay(self, node: defs.Relay, receiver: IReflection) -> IReflection:
		# # receiver
		# var.prop: a.b: A.T
		# var.func_call: a.b(): A.b() -> T
		# relay.prop: a.b.c
		# relay.func_call: a.b.c()
		# func_call.prop: a.b().c
		# func_call.func_call: a.b().c()
		# indexer.prop: a.b[0].c()
		# indexer.func_call: a.b[1].c()

		# AltClass/Nullableを解除
		# XXX Nullable解除に関してはon_relayに到達した時点でnullが期待値であることはあり得ないと言う想定
		unpacked_receiver = self.unpack_alt_class(receiver)
		unpacked_receiver = self.force_unpack_nullable(unpacked_receiver)

		if self.reflections.is_a(unpacked_receiver, type):
			unpacked_receiver = self.unpack_type_proxy(receiver)
			return unpacked_receiver.to(node, self.proc_relay_class(node, unpacked_receiver))
		else:
			return unpacked_receiver.to(node, self.proc_relay_object(node, unpacked_receiver))

	def proc_relay_class(self, node: defs.Relay, receiver: IReflection) -> IReflection:
		prop = self.reflections.type_of_property(receiver.types, node.prop)
		# XXX Enum直下のDeclLocalVarは定数値であり、型としてはEnumそのものであるためreceiverを返却。特殊化より一般化する方法を検討
		if isinstance(receiver.types, defs.Enum) and prop.decl.is_a(defs.DeclLocalVar):
			return receiver
		elif isinstance(prop.decl, defs.Class):
			return self.reflections.type_of_standard(type).stack().extends(prop)
		elif isinstance(prop.decl, defs.Method) and prop.decl.is_property:
			# FIXME クラスのプロパティメソッドは通常存在しないため、修正を検討
			function_helper = template.HelperBuilder(prop) \
				.schema(lambda: {'klass': prop.attrs[0], 'parameters': prop.attrs[1:-1], 'returns': prop.attrs[-1]}) \
				.build(template.Method)
			return function_helper.returns(receiver)
		else:
			return prop

	def proc_relay_object(self, node: defs.Relay, receiver: IReflection) -> IReflection:
		prop = self.reflections.type_of_property(receiver.types, node.prop)
		if isinstance(prop.decl, defs.Method) and prop.decl.is_property:
			function_helper = template.HelperBuilder(prop) \
				.schema(lambda: {'klass': prop.attrs[0], 'parameters': prop.attrs[1:-1], 'returns': prop.attrs[-1]}) \
				.build(template.Method)
			return function_helper.returns(receiver)
		elif isinstance(prop.decl, defs.Class):
			return self.reflections.type_of_standard(type).stack().extends(prop)
		else:
			return prop

	def on_var(self, node: defs.Var) -> IReflection:
		symbol = self.reflections.resolve(node)
		if not symbol.decl.is_a(defs.Class):
			return symbol.stack(node)

		return self.reflections.type_of_standard(type).stack(node).extends(symbol)

	def on_class_ref(self, node: defs.ClassRef) -> IReflection:
		symbol = self.reflections.resolve(node)
		return self.reflections.type_of_standard(type).stack(node).extends(symbol)

	def on_this_ref(self, node: defs.ThisRef) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_indexer(self, node: defs.Indexer, receiver: IReflection, keys: list[IReflection]) -> IReflection:
		unpacked_receiver = self.unpack_alt_class(receiver)

		if node.sliced:
			return unpacked_receiver.stack(node)
		elif self.reflections.is_a(unpacked_receiver, str):
			return unpacked_receiver.stack(node)
		elif self.reflections.is_a(unpacked_receiver, list):
			return unpacked_receiver.to(node, unpacked_receiver.attrs[0])
		elif self.reflections.is_a(unpacked_receiver, dict):
			return unpacked_receiver.to(node, unpacked_receiver.attrs[1])
		elif self.reflections.is_a(unpacked_receiver, tuple):
			if keys[0].node and keys[0].node.is_a(defs.Integer):
				# インデックスが判明している場合はその位置の型を返却
				index = int(keys[0].node.as_a(defs.Integer).tokens)
				return unpacked_receiver.to(node, unpacked_receiver.attrs[index])
			else:
				# インデックスが不明の場合は共用型とする
				return unpacked_receiver.to(node, self.reflections.type_of_standard(classes.Union)).extends(*unpacked_receiver.attrs)
		elif self.reflections.is_a(unpacked_receiver, type):
			# この処理は実質的にCustomTypeの展開と等価
			# XXX 不可解なスタックの解除と追加が連続して意味不明なので修正を検討
			unpacked_receiver = self.unpack_type_proxy(unpacked_receiver)
			unpacked_keys = [self.unpack_type_proxy(key) for key in keys]
			klass_symbol = unpacked_receiver.stack().extends(*unpacked_keys)
			return unpacked_receiver.to(node, self.reflections.type_of_standard(type)).extends(klass_symbol)
		else:
			# XXX コレクション型以外は全て通常のクラスである想定
			# XXX keyに何が入るべきか特定できないためreceiverをそのまま返却
			# XXX この状況で何が取得されるべきかは利用側で判断することとする
			return unpacked_receiver.stack(node)

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: IReflection) -> IReflection:
		"""Note: XXX Pythonではtypeをアンパックする構文が存在しないためAltClassも同様に扱う"""
		return receiver.to(node, self.reflections.type_of_property(receiver.types, node.prop))

	def on_var_of_type(self, node: defs.VarOfType) -> IReflection:
		return self.reflections.resolve(node).stack(node)

	def on_list_type(self, node: defs.ListType, type_name: IReflection, value_type: IReflection) -> IReflection:
		return type_name.stack(node).extends(value_type)

	def on_dict_type(self, node: defs.DictType, type_name: IReflection, key_type: IReflection, value_type: IReflection) -> IReflection:
		return type_name.stack(node).extends(key_type, value_type)

	def on_callable_type(self, node: defs.CallableType, type_name: IReflection, parameters: list[IReflection], return_type: IReflection) -> IReflection:
		return type_name.stack(node).extends(*parameters, return_type)

	def on_custom_type(self, node: defs.CustomType, type_name: IReflection, template_types: list[IReflection]) -> IReflection:
		return type_name.stack(node).extends(*template_types)

	def on_union_type(self, node: defs.UnionType, or_types: list[IReflection]) -> IReflection:
		return self.reflections.type_of_standard(classes.Union).stack(node).extends(*or_types)

	def on_null_type(self, node: defs.NullType) -> IReflection:
		return self.reflections.type_of_standard(None).stack(node)

	def on_func_call(self, node: defs.FuncCall, calls: IReflection, arguments: list[IReflection]) -> IReflection:
		"""
		Note:
			# calls
			* relay: a.b()
			* var: a()
			* indexer: a[0]()
			* func_call: a()()
			# arguments
			* expression
		"""
		actual_calls = self.unpack_alt_class(calls)
		actual_calls = self.unpack_type_proxy(actual_calls)

		if isinstance(actual_calls.types, defs.Class):
			# XXX クラス経由で暗黙的にコンストラクターを呼び出した場合
			# XXX 戻り値の型をクラスのシンボルで補完
			constroctur_calls = self.reflections.type_of_constructor(actual_calls.types)
			function_helper = template.HelperBuilder(constroctur_calls) \
				.schema(lambda: {'klass': constroctur_calls.attrs[0], 'parameters': constroctur_calls.attrs[1:-1], 'returns': actual_calls}) \
				.build(template.Constructor)
			return actual_calls.to(node, function_helper.returns(constroctur_calls.attrs[0], *arguments))
		elif isinstance(actual_calls.types, defs.Constructor):
			# XXX コンストラクターを明示的に呼び出した場合
			# XXX 戻り値の型を第1引数(自己参照)で補完
			function_helper = template.HelperBuilder(actual_calls) \
				.schema(lambda: {'klass': actual_calls.attrs[0], 'parameters': actual_calls.attrs[1:-1], 'returns': actual_calls.attrs[0]}) \
				.build(template.Constructor)
			return actual_calls.to(node, function_helper.returns(actual_calls.attrs[0], *arguments))
		else:
			function_helper = template.HelperBuilder(actual_calls) \
				.case(template.Method).schema(lambda: {'klass': actual_calls.attrs[0], 'parameters': actual_calls.attrs[1:-1], 'returns': actual_calls.attrs[-1]}) \
				.other_case().schema(lambda: {'parameters': actual_calls.attrs[:-1], 'returns': actual_calls.attrs[-1]}) \
				.build(template.Function)
			if function_helper.is_a(template.Method):
				return actual_calls.to(node, function_helper.returns(actual_calls.context, *arguments))
			else:
				return actual_calls.to(node, function_helper.returns(*arguments))

	def on_super(self, node: defs.Super, calls: IReflection, arguments: list[IReflection]) -> IReflection:
		if node.can_resolve_super:
			return calls.to(node, self.reflections.resolve(node.super_class_symbol))
		else:
			return calls.to(node, self.reflections.get_object())

	def on_for_in(self, node: defs.ForIn, iterates: IReflection) -> IReflection:
		"""
		Note:
			# iterates
			## 無視できない
			* list: list<int>
			* dict: dict<str, int>
			* func_call: func<..., T> -> T = list<int> | dict<str, int>
			* var: list<int> | dict<str, int>
			* relay: list<int> | dict<str, int>
			* indexer: list<int> | dict<str, int>
			## 無視してよい
			* group: Any
			* operator: Any
		"""
		iterates = self.unpack_alt_class(iterates)

		def resolve_method() -> tuple[IReflection, str]:
			try:
				return self.reflections.resolve(iterates.types, iterates.types.operations.iterator), 'iterator'
			except UnresolvedSymbolError:
				return self.reflections.resolve(iterates.types, iterates.types.operations.iterable), 'iterable'

		method, solution = resolve_method()
		# XXX iteratorの場合は、戻り値の型をそのまま使用
		# XXX iterableの場合は、戻り値の型が`Iterator<T>`と言う想定でアンパックする
		# XXX # メソッドシグネチャーの期待値
		# XXX `iterator(self) -> T`
		# XXX `iterable(self) -> Iterator<T>`
		schema = {
			'klass': method.attrs[0],
			'parameters': method.attrs[1:-1],
			'returns': method.attrs[-1] if solution == 'iterator' else method.attrs[-1].attrs[0],
		}
		function_helper = template.HelperBuilder(method).schema(lambda: schema).build(template.Method)
		return function_helper.returns(iterates).stack(node)

	def on_comp_for(self, node: defs.CompFor, symbols: list[IReflection], for_in: IReflection) -> IReflection:
		return for_in.stack(node)

	def on_list_comp(self, node: defs.ListComp, projection: IReflection, fors: list[IReflection], condition: IReflection) -> IReflection:
		return projection.to(node, self.reflections.type_of_standard(list)).extends(projection)

	def on_dict_comp(self, node: defs.ListComp, projection: IReflection, fors: list[IReflection], condition: IReflection) -> IReflection:
		return projection.to(node, self.reflections.type_of_standard(dict)).extends(*projection.attrs)

	# Operator

	def on_factor(self, node: defs.Factor, operator: IReflection, value: IReflection) -> IReflection:
		return value.stack(node)

	def on_not_compare(self, node: defs.NotCompare, operator: IReflection, value: IReflection) -> IReflection:
		return value.to(node, self.reflections.type_of_standard(bool))

	def on_or_compare(self, node: defs.OrCompare, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_and_compare(self, node: defs.AndCompare, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_comparison(self, node: defs.Comparison, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_or_bitwise(self, node: defs.OrBitwise, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_xor_bitwise(self, node: defs.XorBitwise, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_and_bitwise(self, node: defs.AndBitwise, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_shift_bitwise(self, node: defs.Sum, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_sum(self, node: defs.Sum, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def on_term(self, node: defs.Term, elements: list[IReflection]) -> IReflection:
		return self.each_binary_operator(node, elements).stack(node)

	def each_binary_operator(self, node: defs.BinaryOperator, elements: list[IReflection]) -> IReflection:
		node_of_elements = node.elements

		operator_indexs = range(1, len(node_of_elements), 2)
		right_indexs = range(2, len(node_of_elements), 2)

		left = elements[0]
		for index, right_index in enumerate(right_indexs):
			operator = node_of_elements[operator_indexs[index]].as_a(defs.Terminal)
			right = elements[right_index]
			left = self.proc_binary_operator(node, left, operator, right)

		return left

	def proc_binary_operator(self, node: defs.BinaryOperator, left: IReflection, operator: defs.Terminal, right: IReflection) -> IReflection:
		operator_name = operator.tokens
		operands: dict[str, IReflection] = {'left': left, 'right': right}
		methods: dict[str, IReflection] = {}
		for key, operand in operands.items():
			try:
				methods[key] = self.reflections.resolve(operand.types, operand.types.operations.operation_by(operator_name))
			except UnresolvedSymbolError:
				pass

		if 'left' not in methods and 'right' not in methods:
			raise OperationNotAllowedError(f'"{operator_name}" not defined. {node}, {str(left)} {operator.tokens} {str(right)}')

		for key, candidate in methods.items():
			if candidate is None:
				continue

			method = candidate
			function_helper = template.HelperBuilder(method) \
				.schema(lambda: {'klass': method.attrs[0], 'parameters': method.attrs[1:-1], 'returns': method.attrs[-1]}) \
				.build(template.Method)

			receiver = left if key == 'left' else right
			other = right if key == 'left' else left
			actual_other = function_helper.parameter(0, receiver, other)

			# XXX 算術演算以外(比較/ビット演算)は返却型が左右で必ず同じであり、戻り値の型の選別が不要であるため省略する
			if not node.is_a(defs.Sum, defs.Term):
				return function_helper.returns(receiver, actual_other)

			var_types = actual_other.attrs if self.reflections.is_a(actual_other, classes.Union) else [actual_other]
			if other in var_types:
				return function_helper.returns(receiver, actual_other)

		raise OperationNotAllowedError(f'Signature not match. {node}, {str(left)} {operator.tokens} {str(right)}')

	def on_tenary_operator(self, node: defs.TenaryOperator, primary: IReflection, condition: IReflection, secondary: IReflection) -> IReflection:
		"""Note: 返却型が一致、またはNullableのみ許可"""
		if primary == secondary:
			return primary.stack(node)

		primary_is_null = self.reflections.is_a(primary, None)
		secondary_is_null = self.reflections.is_a(secondary, None)
		if primary_is_null == secondary_is_null:
			raise OperationNotAllowedError(f'Only Nullable. node: {node}, primary: {primary}, secondary: {secondary}')

		var_type = secondary if primary_is_null else primary
		null_type = primary if primary_is_null else secondary
		return primary.to(node, self.reflections.type_of_standard(classes.Union)).extends(var_type, null_type)

	# Literal

	def on_integer(self, node: defs.Integer) -> IReflection:
		return self.reflections.type_of_standard(int).stack(node)

	def on_float(self, node: defs.Float) -> IReflection:
		return self.reflections.type_of_standard(float).stack(node)

	def on_string(self, node: defs.String) -> IReflection:
		return self.reflections.type_of_standard(str).stack(node)

	def on_doc_string(self, node: defs.DocString) -> IReflection:
		return self.reflections.type_of_standard(str).stack(node)

	def on_truthy(self, node: defs.Truthy) -> IReflection:
		return self.reflections.type_of_standard(bool).stack(node)

	def on_falsy(self, node: defs.Falsy) -> IReflection:
		return self.reflections.type_of_standard(bool).stack(node)

	def on_pair(self, node: defs.Pair, first: IReflection, second: IReflection) -> IReflection:
		return self.reflections.type_of_standard(tuple).stack(node).extends(first, second)

	def on_list(self, node: defs.List, values: list[IReflection]) -> IReflection:
		unknown_type = self.reflections.type_of_standard(classes.Unknown)
		known_types = []
		for index, value in enumerate(values):
			value_type = value if not node.values[index].is_a(defs.Expander) else value.attrs[0]
			if value_type.types != unknown_type.types:
				known_types.append(value_type)

		value_type = known_types[0] if len(known_types) > 0 else unknown_type
		return self.reflections.type_of_standard(list).stack(node).extends(value_type)

	def on_dict(self, node: defs.Dict, items: list[IReflection]) -> IReflection:
		if len(items) == 0:
			unknown_type = self.reflections.type_of_standard(classes.Unknown)
			return self.reflections.type_of_standard(dict).stack(node).extends(unknown_type, unknown_type)
		else:
			unknown_type = self.reflections.type_of_standard(classes.Unknown)
			known_items = [item for item in items if item.attrs[1].types != unknown_type.types]
			item = known_items[0] if len(known_items) > 0 else items[0]
			key_type, value_type = item.attrs
			return self.reflections.type_of_standard(dict).stack(node).extends(key_type, value_type)

	def on_tuple(self, node: defs.Tuple, values: list[IReflection]) -> IReflection:
		return self.reflections.type_of_standard(tuple).stack(node).extends(*values)

	def on_null(self, node: defs.Null) -> IReflection:
		return self.reflections.type_of_standard(None).stack(node)

	# Expression

	def on_group(self, node: defs.Group, expression: IReflection) -> IReflection:
		return expression.stack(node)

	def on_expander(self, node: defs.Expander, expression: IReflection) -> IReflection:
		return expression.stack(node)

	# Terminal

	def on_empty(self, node: defs.Empty) -> IReflection:
		# XXX 厳密にいうとNullとEmptyは別だが、実用上はほぼ同じなので代用
		return self.reflections.type_of_standard(None).stack(node)
