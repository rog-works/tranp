import re
from types import UnionType
from typing import cast

from rogw.tranp.data.version import Versions
from rogw.tranp.dsn.translation import import_dsn
from rogw.tranp.errors import LogicError
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.annotation import implements, injectable
from rogw.tranp.lang.module import fullyname
from rogw.tranp.meta.header import MetaHeader
from rogw.tranp.meta.types import ModuleMetaInjector, TranslatorMeta
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.procedure import Procedure
import rogw.tranp.semantics.reflection.helper.template as template
from rogw.tranp.semantics.reflection.helper.naming import ClassDomainNaming, ClassShorthandNaming
from rogw.tranp.semantics.reflection import IReflection
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.ast.dsn import DSN
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.translator.types import ITranslator, TranslatorOptions
from rogw.tranp.view.render import Renderer


class Py2Cpp(ITranslator):
	"""Python -> C++のトランスパイラー"""

	@injectable
	def __init__(self, reflections: Reflections, render: Renderer, i18n: I18n, module_meta_injector: ModuleMetaInjector, options: TranslatorOptions) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			render (Renderer): ソースレンダー @inject
			i18n (I18n): 国際化対応モジュール @inject
			module_meta_injector (ModuleMetaInjector): モジュールのメタ情報注入 @inject
			options (TranslatorOptions): 実行オプション @inject
		"""
		self.reflections = reflections
		self.view = render
		self.i18n = i18n
		self.module_meta_injector = module_meta_injector
		self.__procedure = self.__make_procedure(options)

	def __make_procedure(self, options: TranslatorOptions) -> Procedure[str]:
		"""プロシージャーを生成

		Args:
			options (TranslatorOptions): 実行オプション
		Returns:
			Procedure[str]: プロシージャー
		"""
		handlers = {key: getattr(self, key) for key in Py2Cpp.__dict__.keys() if key.startswith('on_')}
		procedure = Procedure[str](verbose=options.verbose)
		for key, handler in handlers.items():
			procedure.on(key, handler)

		return procedure

	@property
	@implements
	def meta(self) -> TranslatorMeta:
		"""TranslatorMeta: トランスレーターのメタ情報"""
		return {'version': Versions.py2cpp, 'module': fullyname(Py2Cpp)}

	@implements
	def translate(self, module: Module) -> str:
		"""対象のモジュールを解析してトランスパイル

		Args:
			module (Module): モジュール
		Returns:
			str: トランスパイル後のソースコード
		"""
		return self.__procedure.exec(module.entrypoint)

	def to_accessible_name(self, raw: IReflection) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得 (主にMoveAssignで利用)

		Args:
			raw (IReflection): シンボル
		Returns:
			str: 名前空間上の参照名
		Note:
			# 生成例
			'Class' -> 'NS::Class'
			'dict<A, B>' -> 'dict<NS::A, NS::B>'
		"""
		unpacked_raw = self.force_unpack_nullable(raw)
		shorthand = ClassShorthandNaming.accessible_name(unpacked_raw, alias_handler=self.i18n.t)
		return DSN.join(*DSN.elements(shorthand), delimiter='::')

	def to_domain_name(self, var_type_raw: IReflection) -> str:
		"""明示された型からドメイン名を取得 (主にAnnoAssignで利用)

		Args:
			var_type_raw (IReflection): シンボル
		Returns:
			str: ドメイン名
		Note:
			# 生成例
			'Union<CP<Class>, None>' -> 'Class<CP>'
		"""
		unpacked_raw = self.force_unpack_nullable(var_type_raw)
		return ClassShorthandNaming.domain_name(unpacked_raw, alias_handler=self.i18n.t)

	def to_domain_name_by_class(self, types: defs.ClassDef) -> str:
		"""明示された型からドメイン名を取得

		Args:
			types (ClassDef): クラス宣言ノード
		Returns:
			str: 型の参照名
		"""
		return ClassDomainNaming.domain_name(types, alias_handler=self.i18n.t)

	def force_unpack_nullable(self, symbol: IReflection) -> IReflection:
		"""Nullableのシンボルの変数の型をアンパック。Nullable以外の型はそのまま返却 (主にRelayで利用)

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: 変数の型
		Note:
			許容するNullableの書式 (例: 'Class | None')
			@see ProcedureResolver.force_unpack_nullable
		"""
		if self.reflections.is_a(symbol, UnionType) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.is_a(symbol.attrs[0], None)
			is_1_null = self.reflections.is_a(symbol.attrs[1], None)
			if is_0_null != is_1_null:
				return symbol.attrs[1 if is_0_null else 0]

		return symbol

	def unpack_function_template_types(self, node: defs.Function) -> list[str]:
		"""ファンクションのテンプレート型名をアンパック

		Args:
			node (Function): ファンクションノード
		Returns:
			list[str]: テンプレート型名リスト
		"""
		function_raw = self.reflections.type_of(node)
		function_helper = template.HelperBuilder(function_raw) \
			.case(template.Method).schema(lambda: {'klass': function_raw.attrs[0], 'parameters': function_raw.attrs[1:-1], 'returns': function_raw.attrs[-1]}) \
			.other_case().schema(lambda: {'parameters': function_raw.attrs[1:-1], 'returns': function_raw.attrs[-1]}) \
			.build(template.Function)
		return [types.domain_name for types in function_helper.templates()]

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		meta_header = MetaHeader(self.module_meta_injector(node.module_path), self.meta)
		return self.view.render(node.classification, vars={'statements': statements, 'meta_header': meta_header.to_header_str()})

	# Statement - compound

	def on_else_if(self, node: defs.ElseIf, condition: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements})

	def on_if(self, node: defs.If, condition: str, statements: list[str], else_ifs: list[str], else_statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements, 'else_ifs': else_ifs, 'else_statements': else_statements})

	def on_while(self, node: defs.While, condition: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements})

	def on_for_in(self, node: defs.ForIn, iterates: str) -> str:
		return iterates

	def on_for(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == range.__name__:
			return self.proc_for_range(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == enumerate.__name__:
			return self.proc_for_enumerate(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) and node.iterates.calls.prop.tokens == dict.items.__name__:
			return self.proc_for_dict_items(node, symbols, for_in, statements)
		else:
			return self.view.render(node.classification, vars={'symbols': symbols, 'iterates': for_in, 'statements': statements})

	def proc_for_range(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		last_index = cast(re.Match, re.fullmatch(r'range\((.+)\)', for_in))[1]
		return self.view.render(f'{node.classification}_range', vars={'symbol': symbols[0], 'last_index': last_index, 'statements': statements})

	def proc_for_enumerate(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		iterates = cast(re.Match, re.fullmatch(r'enumerate\((.+)\)', for_in))[1]
		var_type = self.to_accessible_name(self.reflections.type_of(node.for_in).attrs[1])
		return self.view.render(f'{node.classification}_enumerate', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements, 'var_type': var_type})

	def proc_for_dict_items(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		iterates = cast(re.Match, re.fullmatch(r'(.+)\.items\(\)', for_in))[1]
		return self.view.render(f'{node.classification}_dict_items', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements, 'catches': catches})

	def on_comp_for(self, node: defs.CompFor, symbols: list[str], for_in: str) -> str:
		"""Note: XXX range/enumerateは効率・可読性共に非常に悪いため非サポート"""
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == range.__name__:
			raise LogicError(f'Operation not allowed. "range" is not supported. node: {node}')
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == enumerate.__name__:
			raise LogicError(f'Operation not allowed. "enumerate" is not supported. node: {node}')
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) and node.iterates.calls.prop.tokens == dict.items.__name__:
			iterates = cast(re.Match, re.fullmatch(r'(.+)\.items\(\)', for_in))[1]
			return self.view.render(node.classification, vars={'symbols': symbols, 'iterates': iterates})
		else:
			return self.view.render(node.classification, vars={'symbols': symbols, 'iterates': for_in})

	def on_list_comp(self, node: defs.ListComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.reflections.type_of(node.projection)
		projection_type = self.to_accessible_name(projection_type_raw)
		comp_vars = {'projection': projection, 'comp_for': fors[0], 'condition': condition, 'projection_types': [projection_type], 'binded_this': node.binded_this}
		return self.view.render(node.classification, vars=comp_vars)

	def on_dict_comp(self, node: defs.DictComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.reflections.type_of(node.projection)
		projection_type_key = self.to_accessible_name(projection_type_raw.attrs[0])
		projection_type_value = self.to_accessible_name(projection_type_raw.attrs[1])
		comp_vars = {'projection': projection, 'comp_for': fors[0], 'condition': condition, 'projection_types': [projection_type_key, projection_type_value], 'binded_this': node.binded_this}
		return self.view.render(node.classification, vars=comp_vars)

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.unpack_function_template_types(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		return self.view.render(node.classification, vars=function_vars)

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.unpack_function_template_types(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		method_vars = {'access': node.access, 'class_symbol': node.class_types.symbol.tokens}
		return self.view.render(node.classification, vars={**function_vars, **method_vars})

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		this_vars = node.this_vars

		# クラスの初期化ステートメントとそれ以外を分離
		this_var_declares = [this_var.declare.as_a(defs.AnnoAssign) for this_var in this_vars]
		normal_statements: list[str] = []
		initializer_statements: list[str] = []
		super_initializer_statement = ''
		for index, statement in enumerate(node.statements):
			if statement in this_var_declares:
				initializer_statements.append(statements[index])
			elif isinstance(statement, defs.FuncCall) and statement.calls.tokens.endswith('__init__'):
				super_initializer_statement = statements[index]
			else:
				normal_statements.append(statements[index])

		# 親クラスのコンストラクター呼び出しのデータを生成
		super_initializer = {}
		if super_initializer_statement:
			super_initializer['parent'] = super_initializer_statement.split('::')[0]
			# XXX コンストラクターへの実引数を取得。必ず取得できるのでキャストして警告を抑制 (期待値: `Class::__init__(a, b, c);`)
			super_initializer['arguments'] = cast(re.Match[str], re.search(r'\(([^)]*)\);$', super_initializer_statement))[1]

		# メンバー変数の宣言用のデータを生成
		initializers: list[dict[str, str]] = []
		for index, this_var in enumerate(this_vars):
			# XXX 代入式の右辺を取得。必ず取得できるのでキャストして警告を抑制 (期待値: `int this->a = 1234;`)
			initialize_value = cast(re.Match[str], re.search(r'=\s*([^;]+);$', initializer_statements[index]))[1]
			this_var_name = this_var.tokens_without_this
			initializers.append({'symbol': this_var_name, 'value': initialize_value})

		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = self.unpack_function_template_types(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': normal_statements, 'template_types': template_types}
		method_vars = {'access': node.access, 'class_symbol': class_name}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(node.classification, vars={**function_vars, **method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.unpack_function_template_types(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		method_vars = {'access': node.access, 'class_symbol': node.class_types.symbol.tokens}
		return self.view.render(node.classification, vars={**function_vars, **method_vars})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		"""Note: closureでtemplate_typesは不要なので対応しない"""
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'statements': statements}
		closure_vars = {'binded_this': node.binded_this}
		return self.view.render(node.classification, vars={**function_vars, **closure_vars})

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], generic_types: list[str], comment: str, statements: list[str]) -> str:
		# XXX クラス変数とそれ以外のステートメントを分離
		decl_class_var_statements: list[str] = []
		other_statements: list[str] = []
		for index, statement in enumerate(node.statements):
			if isinstance(statement, defs.AnnoAssign):
				decl_class_var_statements.append(statements[index])
			else:
				other_statements.append(statements[index])

		# XXX メンバー変数の展開方法を検討
		vars: list[str] = []
		for index, class_var in enumerate(node.class_vars):
			class_var_name = class_var.tokens
			class_var_vars = {'access': defs.to_access(class_var_name), 'decl_class_var': decl_class_var_statements[index]}
			vars.append(self.view.render('class_decl_class_var', vars=class_var_vars))

		for this_var in node.this_vars:
			this_var_name = this_var.tokens_without_this
			var_type_raw = self.reflections.type_of(this_var.declare.as_a(defs.AnnoAssign).var_type)
			var_type = self.to_domain_name(var_type_raw)
			this_var_vars = {'access': defs.to_access(this_var_name), 'symbol': this_var_name, 'var_type': var_type}
			vars.append(self.view.render('class_decl_this_var', vars=this_var_vars))

		class_vars = {'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'generic_types': generic_types, 'comment': comment, 'statements': other_statements, 'vars': vars}
		return self.view.render(node.classification, vars=class_vars)

	def on_enum(self, node: defs.Enum, symbol: str, decorators: list[str], inherits: list[str], generic_types: list[str], comment: str, statements: list[str]) -> str:
		add_vars = {}
		if not node.parent.is_a(defs.Entrypoint):
			add_vars = {'access': node.access}

		return self.view.render(node.classification, vars={'symbol': symbol, 'comment': comment, 'statements': statements, **add_vars})

	def on_alt_class(self, node: defs.AltClass, symbol: str, actual_type: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'actual_type': actual_type})

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})

	def on_decorator(self, node: defs.Decorator, path: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'path': path, 'arguments': arguments})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		if len(receivers) == 1:
			return self.proc_move_assign_single(node, receivers[0], value)
		else:
			return self.proc_move_assign_unpack(node, receivers, value)

	def proc_move_assign_single(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		receiver_raw = self.reflections.type_of(node.receivers[0])
		value_raw = self.reflections.type_of(node.value)
		declared = receiver_raw.decl.declare == node
		var_type = self.to_accessible_name(value_raw) if declared else ''
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def proc_move_assign_unpack(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		return self.view.render(f'{node.classification}_unpack', vars={'receivers': receivers, 'value': value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, operator: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'operator': operator, 'value': value})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		return self.view.render(node.classification, vars={'return_value': return_value})

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(node.classification, vars={'throws': throws, 'via': via})

	def on_pass(self, node: defs.Pass) -> None:
		pass

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_comment(self, node: defs.Comment) -> str:
		return f'//{node.text}'

	def on_import(self, node: defs.Import, symbols: list[str]) -> str:
		"""
		Note:
			* 通常、インポートは全てコメントアウトして出力
			* 翻訳データにインポート置換用のDSNを登録することで、その行のみ有効な行として出力を変更
			@see dsn.translation.import_dsn
			@see i18n.I18n.t
		"""
		module_path = node.import_path.tokens
		text = self.view.render(node.classification, vars={'module_path': module_path})
		return self.i18n.t(import_dsn(module_path), text)

	# Primary

	def on_decl_class_var(self, node: defs.DeclClassVar) -> str:
		return node.tokens

	def on_decl_this_var(self, node: defs.DeclThisVar) -> str:
		return node.tokens.replace('self.', 'this->')

	def on_decl_class_param(self, node: defs.DeclClassParam) -> str:
		return node.tokens

	def on_decl_this_param(self, node: defs.DeclThisParam) -> str:
		return node.tokens

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> str:
		return node.tokens

	def on_types_name(self, node: defs.TypesName) -> str:
		return self.to_domain_name_by_class(node.class_types.as_a(defs.ClassDef))

	def on_import_name(self, node: defs.ImportName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		receiver_symbol = self.reflections.type_of(node.receiver)
		receiver_symbol = self.force_unpack_nullable(receiver_symbol)
		prop_symbol = self.reflections.type_of_property(receiver_symbol.types, node.prop)
		prop = node.prop.domain_name
		if isinstance(prop_symbol.decl, defs.ClassDef):
			prop = self.to_domain_name_by_class(prop_symbol.types)

		spec, accessor = self.analyze_relay_access_spec(node, receiver_symbol)
		relay_vars = {'receiver': receiver, 'accessor': accessor, 'prop': prop}
		if spec == 'cvar_on':
			cvar_receiver = re.sub(rf'(->|::|\.){CVars.relay_key}$', '', receiver)
			return self.view.render(node.classification, vars={**relay_vars, 'receiver': cvar_receiver})
		elif spec.startswith('cvar_to_'):
			cvar_receiver = re.sub(rf'(->|::|\.)({"|".join(CVars.exchanger_keys)})$', '', receiver)
			move = spec.split('cvar_to_')[1]
			return self.view.render(f'{node.classification}_cvar_to', vars={**relay_vars, 'receiver': cvar_receiver, 'move': move})
		else:
			return self.view.render(node.classification, vars=relay_vars)

	def analyze_relay_access_spec(self, node: defs.Relay, receiver_symbol: IReflection) -> tuple[str, str]:
		def is_this_access() -> bool:
			return node.receiver.is_a(defs.ThisRef)

		def is_on_cvar_relay() -> bool:
			return isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.relay_key

		def is_on_cvar_exchanger() -> bool:
			return node.prop.domain_name in CVars.exchanger_keys

		def is_class_access() -> bool:
			# XXX superは一般的には親クラスのインスタンスへの参照だが、C++ではクラス参照と同じ修飾子によってアクセスするため、例外的に判定に加える
			is_class_alias = isinstance(node.receiver, (defs.ClassRef, defs.Super))
			is_class_var_relay = node.receiver.is_a(defs.Relay, defs.Var) and receiver_symbol.decl.is_a(defs.Class)
			return is_class_alias or is_class_var_relay

		if is_this_access():
			return 'this', CVars.Accessors.Address.name
		elif is_on_cvar_relay():
			cvar_key = CVars.key_from(self.reflections, receiver_symbol.context)
			if not CVars.is_raw_raw(cvar_key):
				return 'cvar_on', CVars.to_accessor(cvar_key).name
		elif is_on_cvar_exchanger():
			cvar_key = CVars.key_from(self.reflections, receiver_symbol)
			move = CVars.to_move(cvar_key, node.prop.domain_name)
			if not CVars.is_raw_raw(cvar_key):
				return f'cvar_to_{move.name}', CVars.to_accessor(cvar_key).name
		elif is_class_access():
			return 'class', CVars.Accessors.Static.name

		return 'raw', CVars.Accessors.Raw.name

	def on_class_ref(self, node: defs.ClassRef) -> str:
		return node.class_symbol.tokens

	def on_this_ref(self, node: defs.ThisRef) -> str:
		return 'this'

	def on_argument_label(self, node: defs.ArgumentLabel) -> str:
		return node.tokens

	def on_var(self, node: defs.Var) -> str:
		symbol = self.reflections.type_of(node)
		if isinstance(symbol.decl, defs.ClassDef):
			return self.to_domain_name_by_class(symbol.types)
		else:
			return node.tokens

	def on_indexer(self, node: defs.Indexer, receiver: str, key: str) -> str:
		spec = self.analyze_indexer_spec(node)
		if spec == 'cvar_on':
			cvar_receiver = re.sub(rf'(->|::|\.){CVars.relay_key}$', '', receiver)
			return self.view.render(node.classification, vars={'receiver': cvar_receiver, 'key': key})
		else:
			return self.view.render(node.classification, vars={'receiver': receiver, 'key': key})

	def analyze_indexer_spec(self, node: defs.Indexer) -> str:
		def is_on_cvar_relay() -> bool:
			return isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.relay_key

		if is_on_cvar_relay():
			receiver_symbol = self.reflections.type_of(node.receiver)
			cvar_key = CVars.key_from(self.reflections, receiver_symbol.context)
			if not CVars.is_raw_raw(cvar_key):
				return 'cvar_on'

		return 'otherwise'

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: str) -> str:
		receiver_symbol = self.reflections.type_of(node.receiver)
		prop_symbol = self.reflections.type_of_property(receiver_symbol.types, node.prop)
		type_name = self.to_domain_name_by_class(prop_symbol.types)
		return self.view.render(node.classification, vars={'receiver': receiver, 'type_name': type_name})

	def on_var_of_type(self, node: defs.VarOfType) -> str:
		symbol = self.reflections.type_of(node)
		type_name = self.to_domain_name_by_class(symbol.types)
		return self.view.render(node.classification, vars={'type_name': type_name})

	def on_list_type(self, node: defs.ListType, type_name: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_callable_type(self, node: defs.CallableType, type_name: str, parameters: list[str], return_type: str) -> str:
		raise NotImplementedError(f'Not supported CallableType. symbol: {node.fullyname}')

	def on_custom_type(self, node: defs.CustomType, type_name: str, template_types: list[str]) -> str:
		# XXX @see Symbol.make_shorthand
		return self.view.render('type_py2cpp', vars={'var_type': f'{type_name}<{", ".join(template_types)}>'})

	def on_union_type(self, node: defs.UnionType, or_types: list[str]) -> str:
		"""
		Note:
			Union型はNullableのみ許可 (変換例: 'CP[Class] | None' -> 'Class*'
			@see CVars.__resolve_var_type
		"""
		if len(node.or_types) != 2:
			raise LogicError(f'Unexpected UnionType. expected 2 types. symbol: {node.fullyname}, got: {len(node.or_types)}')

		is_0_null = node.or_types[0].is_a(defs.NullType)
		is_1_null = node.or_types[1].is_a(defs.NullType)
		if is_0_null == is_1_null:
			raise LogicError(f'Unexpected UnionType. with not nullable. symbol: {node.fullyname}, or_types: [{or_types[0]}, {or_types[1]}]')

		var_type_index = 1 if is_0_null else 0
		var_type_node = node.or_types[var_type_index]
		is_addr_p = isinstance(var_type_node, defs.CustomType) and CVars.is_addr_p(var_type_node.domain_name)
		if not is_addr_p:
			raise LogicError(f'Unexpected UnionType. with not pointer. symbol: {node.fullyname}, var_type: {var_type_node}')

		return or_types[var_type_index]

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block)
		spec, context = self.analyze_func_call_spec(node, calls)
		func_call_vars = {'calls': calls, 'arguments': arguments, 'is_statement': is_statement}
		if spec == 'directive':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'len':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'print':
			# XXX 愚直に対応すると実引数の型推論のコストが高く、その割に出力メッセージの柔軟性が下がりメリットが薄いため、関数名の置き換えのみを行う簡易的な対応とする
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'new_list':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'cast_bin_to_bin':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_str_to_bin':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_bin_to_str':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'list_pop':
			receiver = re.sub(r'(->|::|\.)pop$', '', calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': receiver, 'var_type': var_type})
		elif spec == 'dict_pop':
			receiver = re.sub(r'(->|::|\.)pop$', '', calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': receiver, 'var_type': var_type})
		elif spec == 'dict_keys':
			receiver = re.sub(r'(->|::|\.)keys$', '', calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': receiver, 'var_type': var_type})
		elif spec == 'dict_values':
			receiver = re.sub(r'(->|::|\.)values$', '', calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': receiver, 'var_type': var_type})
		elif spec == 'new_enum':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}_cast_bin_to_bin', vars={**func_call_vars, 'var_type': var_type})
		elif spec.startswith('to_cvar_'):
			cvar_type = spec.split('to_cvar_')[1]
			return self.view.render(f'{node.classification}_to_cvar', vars={**func_call_vars, 'cvar_type': cvar_type})
		elif spec == 'new_cvar_p':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'new_cvar_sp_list':
			var_type = self.to_accessible_name(cast(IReflection, context))
			initializer = arguments[0]
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		elif spec == 'new_cvar_sp':
			var_type = self.to_accessible_name(cast(IReflection, context))
			initializer = cast(re.Match, re.fullmatch(r'[^(]+\(([^)]+)\)', arguments[0]))[1]
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		else:
			return self.view.render(node.classification, vars=func_call_vars)

	def analyze_func_call_spec(self, node: defs.FuncCall, calls: str) -> tuple[str, IReflection | None]:
		"""
		Note:
			FIXME callsは__alias__によって別名になる可能性があるため、実装名が欲しい場合はノードから直接取得すること。全体的な見直しが必要かも
		"""
		if calls == 'directive':
			return 'directive', None
		elif calls == 'len':
			return 'len', None
		elif calls == 'print':
			return 'print', None
		elif isinstance(node.calls, defs.Var) and node.calls.tokens == 'list':
			return 'new_list', None
		elif isinstance(node.calls, defs.Var) and node.calls.tokens in ['int', 'float', 'bool', 'str']:
			org_calls = node.calls.tokens
			casted_types = {'int': int, 'float': float, 'bool': bool, 'str': str}
			from_raw = self.reflections.type_of(node.arguments[0])
			to_type = casted_types[org_calls]
			to_raw = self.reflections.type_of_standard(to_type)
			if self.reflections.is_a(from_raw, str):
				return 'cast_str_to_bin', to_raw
			elif to_type == str:
				return 'cast_bin_to_str', from_raw
			else:
				return 'cast_bin_to_bin', to_raw
		elif isinstance(node.calls, defs.Relay) and node.calls.prop.tokens in ['pop', 'keys', 'values']:
			prop = node.calls.prop.tokens
			context = self.reflections.type_of(node.calls).context
			if self.reflections.is_a(context, list) and prop == 'pop':
				return 'list_pop', context.attrs[0]
			elif self.reflections.is_a(context, dict) and prop in ['pop', 'keys', 'values']:
				key_attr, value_attr = context.attrs
				attr_indexs = {'pop': value_attr, 'keys': key_attr, 'values': value_attr}
				return f'dict_{prop}', attr_indexs[prop]
		elif isinstance(node.calls, defs.Var) and node.calls.tokens in CVars.keys():
			return f'to_cvar_{node.calls.tokens}', None
		elif isinstance(node.calls, defs.Relay) and node.calls.prop.tokens == CVars.allocator_key:
			context = self.reflections.type_of(node.calls).context
			cvar_key = CVars.key_from(self.reflections, context)
			if CVars.is_addr_p(cvar_key):
				return f'new_cvar_p', None
			elif CVars.is_addr_sp(cvar_key):
				new_type_raw = self.reflections.type_of(node.arguments[0])
				spec = 'new_cvar_sp_list' if self.reflections.is_a(new_type_raw, list) else 'new_cvar_sp'
				return spec, new_type_raw
		elif isinstance(node.calls, (defs.Relay, defs.Var)):
			raw = self.reflections.type_of(node.calls)
			if raw.types.is_a(defs.Enum):
				return 'new_enum', raw

		return 'otherwise', None

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		return node.super_class_symbol.tokens

	def on_argument(self, node: defs.Argument, label: str, value: str) -> str:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: str) -> str:
		return class_type

	# Operator

	def on_factor(self, node: defs.Factor, operator: str, value: str) -> str:
		return self.view.render('unary_operator', vars={'operator': operator, 'value': value})

	def on_not_compare(self, node: defs.NotCompare, operator: str, value: str) -> str:
		return self.view.render('unary_operator', vars={'operator': '!', 'value': value})

	def on_or_compare(self, node: defs.OrCompare, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_and_compare(self, node: defs.AndCompare, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_comparison(self, node: defs.Comparison, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_or_bitwise(self, node: defs.OrBitwise, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_xor_bitwise(self, node: defs.XorBitwise, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_and_bitwise(self, node: defs.AndBitwise, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_sum(self, node: defs.Sum, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def on_term(self, node: defs.Term, elements: list[str]) -> str:
		return self.proc_binary_operator(node, elements)

	def proc_binary_operator(self, node: defs.BinaryOperator, elements: list[str]) -> str:
		node_of_elements = node.elements

		# インデックスを算出
		operator_indexs = range(1, len(node_of_elements), 2)
		right_indexs = range(2, len(node_of_elements), 2)

		# シンボルを解決
		primary_raw = self.reflections.type_of(node_of_elements[0])
		secondary_raws = [self.reflections.type_of(node_of_elements[index]) for index in right_indexs]

		# 項目ごとに分離
		primary = elements[0]
		operators = [elements[index] for index in operator_indexs]
		secondaries = [elements[index] for index in right_indexs]

		list_is_primary = self.reflections.is_a(primary_raw, list)
		list_is_secondary = self.reflections.is_a(secondary_raws[0], list)
		if list_is_primary != list_is_secondary and operators[0] == '*':
			default_raw, default = (primary_raw, primary) if list_is_primary else (secondary_raws[0], secondaries[0])
			size_raw, size = (secondary_raws[0], secondaries[0]) if list_is_primary else (primary_raw, primary)
			return self.proc_binary_operator_fill_list(node, default_raw, size_raw, default, size)
		else:
			return self.proc_binary_operator_expression(node, primary_raw, secondary_raws, primary, operators, secondaries)

	def proc_binary_operator_fill_list(self, node: defs.BinaryOperator, default_raw: IReflection, size_raw: IReflection, default: str, size: str) -> str:
		value_type = self.to_accessible_name(default_raw.attrs[0])
		# 必ず要素1の配列のリテラルになるので、defaultの前後の括弧を除外する FIXME 現状仕様を前提にした処理なので妥当性が低い
		return self.view.render('binary_operator_fill_list', vars={'value_type': value_type, 'default': default[1:-1], 'size': size})

	def proc_binary_operator_expression(self, node: defs.BinaryOperator, left_raw: IReflection, right_raws: list[IReflection], left: str, operators: list[str], rights: list[str]) -> str:
		primary = left
		for index, right_raw in enumerate(right_raws):
			operator = operators[index]
			secondary = rights[index]
			primary = self.view.render('binary_operator', vars={'left': primary, 'operator': operator, 'right': secondary, 'right_is_dict': self.reflections.is_a(right_raw, dict)})

		return primary

	def on_tenary_operator(self, node: defs.TenaryOperator, primary: str, condition: str, secondary: str) -> str:
		return self.view.render(node.classification, vars={'primary': primary, 'condition': condition, 'secondary': secondary})

	# Literal

	def on_string(self, node: defs.String) -> str:
		return node.tokens.replace("'", '"')

	def on_doc_string(self, node: defs.DocString) -> str:
		return self.view.render(node.classification, vars={'data': node.data})

	def on_truthy(self, node: defs.Truthy) -> str:
		return 'true'

	def on_falsy(self, node: defs.Falsy) -> str:
		return 'false'

	def on_pair(self, node: defs.Pair, first: str, second: str) -> str:
		return '{' f'{first}, {second}' '}'

	def on_list(self, node: defs.List, values: list[str]) -> str:
		return self.view.render(node.classification, vars={'values': values})

	def on_dict(self, node: defs.Dict, items: list[str]) -> str:
		return self.view.render(node.classification, vars={'items': items})

	def on_null(self, node: defs.Null) -> str:
		return 'nullptr'

	# Expression

	def on_group(self, node: defs.Group, expression: str) -> str:
		return f'({expression})'

	# Terminal

	def on_terminal(self, node: Node) -> str:
		return node.tokens

	# Fallback

	def on_fallback(self, node: Node) -> str:
		return node.tokens
