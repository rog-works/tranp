import re
from typing import Any, Self, TypeVarTuple, cast

from rogw.tranp.compatible.cpp.embed import Embed
from rogw.tranp.compatible.cpp.object import CP, c_func_addr, c_func_ref
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory, TranspilerMeta
from rogw.tranp.data.version import Versions
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.translation import alias_dsn, import_dsn
from rogw.tranp.errors import LogicError
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.annotation import duck_typed, implements, injectable
from rogw.tranp.lang.eventemitter import Callback, Observable
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.lang.parser import BlockFormatter, BlockParser
from rogw.tranp.semantics.errors import NotSupportedError
from rogw.tranp.semantics.procedure import Procedure
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.semantics.reflection.definition as refs
from rogw.tranp.semantics.reflection.helper.naming import ClassDomainNaming, ClassShorthandNaming
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.definition.accessible import PythonClassOperations
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.transpiler.types import ITranspiler, TranspilerOptions
from rogw.tranp.view.render import Renderer


class Py2Cpp(ITranspiler):
	"""Python -> C++のトランスパイラー"""

	@injectable
	def __init__(self, reflections: Reflections, render: Renderer, i18n: I18n, module_meta_factory: ModuleMetaFactory, options: TranspilerOptions) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			render (Renderer): ソースレンダー @inject
			i18n (I18n): 国際化対応モジュール @inject
			module_meta_factory (ModuleMetaFactory): モジュールのメタ情報ファクトリー @inject
			options (TranslatorOptions): 実行オプション @inject
		"""
		self.reflections = reflections
		self.view = render
		self.i18n = i18n
		self.module_meta_factory = module_meta_factory
		self.__procedure = self.__make_procedure(options)

	def __make_procedure(self, options: TranspilerOptions) -> Procedure[str]:
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

	@duck_typed(Observable)
	def on(self, action: str, callback: Callback[str]) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): アクション名
			callback (Callback[str]): ハンドラー
		"""
		self.__procedure.on(action, callback)

	@duck_typed(Observable)
	def off(self, action: str, callback: Callback[str]) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): アクション名
			callback (Callback[str]): ハンドラー
		"""
		self.__procedure.off(action, callback)

	@property
	@implements
	def meta(self) -> TranspilerMeta:
		"""TranspilerMeta: トランスパイラーのメタ情報"""
		return {'version': Versions.py2cpp, 'module': to_fullyname(Py2Cpp)}

	@implements
	def transpile(self, root: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			root (Node): 起点のノード
		Returns:
			str: トランスパイル後のソースコード
		"""
		return self.__procedure.exec(root)

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
			'CP<A>' -> 'NS::A*'
		"""
		actual_raw = raw.impl(refs.Object).actualize('nullable')
		shorthand = ClassShorthandNaming.accessible_name(actual_raw, alias_handler=self.i18n.t)

		# C++型変数の表記変換
		if len([True for key in CVars.keys() if key in shorthand]) > 0:
			def formatter(entry: BlockFormatter) -> str | None:
				var_type = entry.block(alt_formatter=formatter)
				return self.view.render('type_py2cpp', vars={'var_type': var_type})

			shorthand = BlockParser.parse_to_formatter(shorthand, '<>', ',').format(alt_formatter=formatter)

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
		actual_type_raw = var_type_raw.impl(refs.Object).actualize('nullable')
		return ClassShorthandNaming.domain_name(actual_type_raw, alias_handler=self.i18n.t)

	def to_domain_name_by_class(self, types: defs.ClassDef) -> str:
		"""明示された型からドメイン名を取得

		Args:
			types (ClassDef): クラス宣言ノード
		Returns:
			str: 型の参照名
		"""
		return ClassDomainNaming.domain_name(types, alias_handler=self.i18n.t)

	def fetch_function_template_names(self, node: defs.Function) -> list[str]:
		"""ファンクションのテンプレート型名を取得

		Args:
			node (Function): ファンクションノード
		Returns:
			list[str]: テンプレート型名リスト
		"""
		return [types.domain_name for types in self.reflections.type_of(node).impl(refs.Function).function_templates()]

	def allow_override_from_method(self, method: defs.ClassMethod | defs.Constructor | defs.Method) -> bool:
		"""仮想関数の判定

		Args:
			method (Constructur | Method): メソッド系ノード
		Returns:
			bool: True = 仮想関数
		Note:
			C++ではClassMethodの仮想関数はないので非対応
		"""
		return len([decorator for decorator in method.decorators if decorator.path.tokens == f'{Embed.__name__}.{Embed.allow_override.__name__}']) > 0

	def to_accessor(self, accessor: str) -> str:
		"""アクセス修飾子を翻訳

		Args:
			accessor (str): アクセス修飾子
		Returns:
			str: 翻訳後のアクセス修飾子
		"""
		return self.i18n.t(DSN.join(self.i18n.t(alias_dsn('lang')), 'accessor', accessor))

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		meta_header = MetaHeader(self.module_meta_factory(node.module_path), self.meta)
		return self.view.render(node.classification, vars={'statements': statements, 'meta_header': meta_header.to_header_str(), 'module_path': node.module_path})

	# Statement - compound

	def on_else_if(self, node: defs.ElseIf, condition: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements})

	def on_else(self, node: defs.Else, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements})

	def on_if(self, node: defs.If, condition: str, statements: list[str], else_ifs: list[str], else_clause: str) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements, 'else_ifs': else_ifs, 'else_clause': else_clause})

	def on_while(self, node: defs.While, condition: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements})

	def on_for(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == range.__name__:
			return self.proc_for_range(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == enumerate.__name__:
			return self.proc_for_enumerate(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) and node.iterates.calls.prop.tokens == dict.items.__name__:
			return self.proc_for_dict_items(node, symbols, for_in, statements)
		else:
			for_in_symbol = self.reflections.type_of(node.for_in)
			# FIXME is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
			is_const = CVars.is_const(CVars.key_from(for_in_symbol))
			is_addr_p = CVars.is_addr_p(CVars.key_from(for_in_symbol))
			return self.view.render(f'{node.classification}/default', vars={'symbols': symbols, 'iterates': for_in, 'statements': statements, 'is_const': is_const, 'is_addr_p': is_addr_p})

	def proc_for_range(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# 期待値: 'range(arguments...)'
		last_index = PatternParser.pluck_func_call_arguments(for_in)
		return self.view.render(f'{node.classification}/range', vars={'symbol': symbols[0], 'last_index': last_index, 'statements': statements})

	def proc_for_enumerate(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# 期待値: 'enumerate(arguments...)'
		iterates = PatternParser.pluck_func_call_arguments(for_in)
		var_type = self.to_accessible_name(self.reflections.type_of(node.for_in).attrs[1])
		return self.view.render(f'{node.classification}/enumerate', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements, 'var_type': var_type})

	def proc_for_dict_items(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# 期待値: 'iterates.items()'
		iterates = PatternParser.pluck_dict_items_receiver(for_in)
		# XXX 参照の変換方法が場当たり的で一貫性が無い。包括的な対応を検討
		iterates = f'*({iterates})' if for_in.endswith('->items()') else iterates
		return self.view.render(f'{node.classification}/dict_items', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements, 'catches': catches})

	def on_with_entry(self, node: defs.WithEntry, enter: str, symbol: str) -> str:
		raise NotSupportedError(f'Denied with statement. node: {node}')

	def on_with(self, node: defs.With, statements: list[str], entries: list[str]) -> str:
		raise NotSupportedError(f'Denied with statement. node: {node}')

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.fetch_function_template_names(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		return self.view.render(f'function/{node.classification}', vars=function_vars)

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.fetch_function_template_names(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'class_symbol': node.class_types.symbol.tokens}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars})

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
			# 期待値: `Class::__init__(a, b, c);`
			super_initializer['arguments'] = PatternParser.pluck_super_arguments(super_initializer_statement)

		# メンバー変数の宣言用のデータを生成
		initializers: list[dict[str, str]] = []
		for index, this_var in enumerate(this_vars):
			# 期待値: `int this->a = 1234;`
			initial_value = PatternParser.pluck_assign_right(initializer_statements[index])
			initializer = {'symbol': self.i18n.t(alias_dsn(this_var.fullyname), this_var.domain_name), 'value': initial_value}
			initializers.append(initializer)

		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = self.fetch_function_template_names(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': normal_statements, 'template_types': template_types}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'class_symbol': class_name, 'allow_override': self.allow_override_from_method(node)}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = self.fetch_function_template_names(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'class_symbol': node.class_types.symbol.tokens, 'allow_override': self.allow_override_from_method(node)}
		special_specs = {PythonClassOperations.copy_constructor: 'copy_constructor', PythonClassOperations.destructor: 'destructor'}
		spec = special_specs.get(symbol, node.classification)
		return self.view.render(f'function/{spec}', vars={**function_vars, **method_vars})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		"""Note: closureでtemplate_typesは不要なので対応しない"""
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'statements': statements}
		return self.view.render(f'function/{node.classification}', vars=function_vars)

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		# XXX 構造体の判定
		is_struct = len([decorator for decorator in decorators if decorator.startswith(f'{Embed.__name__}.{Embed.struct.__name__}')])

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
			class_var_vars = {'accessor': self.to_accessor(defs.to_accessor(class_var_name)), 'decl_class_var': decl_class_var_statements[index], 'decorators': decorators}
			vars.append(self.view.render(f'{node.classification}/_decl_class_var', vars=class_var_vars))

		for this_var in node.this_vars:
			this_var_name = this_var.tokens_without_this
			# XXX 再帰的なトランスパイルで型名を解決
			var_type = self.transpile(this_var.declare.as_a(defs.AnnoAssign).var_type)
			this_var_vars = {'accessor': self.to_accessor(defs.to_accessor(this_var_name)), 'symbol': this_var_name, 'var_type': var_type, 'decorators': decorators}
			vars.append(self.view.render(f'{node.classification}/_decl_this_var', vars=this_var_vars))

		class_vars = {'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'template_types': template_types, 'comment': comment, 'statements': other_statements, 'vars': vars, 'is_struct': is_struct}
		return self.view.render(f'{node.classification}/class', vars=class_vars)

	def on_enum(self, node: defs.Enum, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		add_vars = {}
		if not node.parent.is_a(defs.Entrypoint):
			add_vars = {'accessor': self.to_accessor(node.accessor)}

		return self.view.render(f'class/{node.classification}', vars={'symbol': symbol, 'decorators': decorators, 'comment': comment, 'statements': statements, **add_vars})

	def on_alt_class(self, node: defs.AltClass, symbol: str, actual_type: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'actual_type': actual_type})

	def on_template_class(self, node: defs.TemplateClass, symbol: str) -> str:
		return f'// template<typename {symbol}>'

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		# Selfの型注釈がかえって邪魔なため削除 FIXME 型の情報を消す必然性が見えない。修正を検討
		if isinstance(node.declare.symbol, (defs.DeclClassParam, defs.DeclThisParam)):
			var_type = ''

		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})

	def on_decorator(self, node: defs.Decorator, path: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'path': path, 'arguments': arguments})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		if len(receivers) == 1:
			return self.proc_move_assign_single(node, receivers[0], value)
		else:
			return self.proc_move_assign_destruction(node, receivers, value)

	def proc_move_assign_single(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		receiver_raw = self.reflections.type_of(node.receivers[0])
		value_raw = self.reflections.type_of(node.value)
		declared = receiver_raw.decl.declare == node
		var_type = self.to_accessible_name(value_raw)
		receiver_is_dict = isinstance(node.receivers[0], defs.Indexer) and self.reflections.type_of(node.receivers[0].receiver).impl(refs.Object).type_is(dict)
		return self.view.render(f'assign/{node.classification}', vars={'receiver': receiver, 'var_type': var_type, 'value': value, 'declared': declared, 'receiver_is_dict': receiver_is_dict})

	def proc_move_assign_destruction(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		"""Note: C++で分割代入できるのはtuple/pairのみ。Pythonではいずれもtupleのため、tuple以外は非対応"""
		value_raw = self.reflections.type_of(node.value).impl(refs.Object).actualize()
		if not value_raw.type_is(tuple):
			raise LogicError(f'Not allowed destruction assign. value must be a tuple. node: {node}')

		return self.view.render(f'assign/{node.classification}_destruction', vars={'receivers': receivers, 'value': value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		return self.view.render(f'assign/{node.classification}', vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, value: str) -> str:
		return self.view.render(f'assign/{node.classification}', vars={'receiver': receiver, 'operator': node.operator.tokens, 'value': value})

	def on_delete(self, node: defs.Delete, targets: str) -> str:
		target_types: list[str] = []
		for target_node in node.targets:
			if not isinstance(target_node, defs.Indexer):
				raise LogicError(f'Unexpected delete target. supported type is list or dict. target: {target_node}')

			target_symbol = self.reflections.type_of(target_node.receiver)
			target_types.append('list' if target_symbol.impl(refs.Object).type_is(list) else 'dict')

		_targets: list[dict[str, str]] = []
		for i in range(len(targets)):
			target = targets[i]
			receiver, key = PatternParser.break_indexer(target)
			_targets.append({'receiver': receiver, 'key': key, 'list_or_dict': target_types[i]})

		return self.view.render(f'{node.classification}/default', vars={'targets': _targets})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		return self.view.render(node.classification, vars={'return_value': return_value})

	def on_yield(self, node: defs.Yield, yield_value: str) -> str:
		raise NotSupportedError(f'Denied yield return. node: {node}')

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(node.classification, vars={'throws': throws, 'via': via})

	def on_pass(self, node: defs.Pass) -> str:
		# XXX statementsのスタック数が合わなくなるため出力
		return ''

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

	def on_argument(self, node: defs.Argument, label: str, value: str) -> str:
		return self.view.render(node.classification, vars={'label': label, 'value': value})

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: str) -> str:
		return class_type

	def on_argument_label(self, node: defs.ArgumentLabel) -> str:
		return node.tokens

	def on_decl_class_var(self, node: defs.DeclClassVar) -> str:
		return self.i18n.t(alias_dsn(node.fullyname), node.tokens)

	def on_decl_this_var_forward(self, node: defs.DeclThisVarForward) -> str:
		"""Note: XXX いずれにせよ出力されないので翻訳は対応不要"""
		return node.tokens

	def on_decl_this_var(self, node: defs.DeclThisVar) -> str:
		prop_name = self.i18n.t(alias_dsn(node.fullyname), node.domain_name)
		return f'this->{prop_name}'

	def on_decl_local_var(self, node: defs.DeclLocalVar) -> str:
		return node.tokens

	def on_decl_class_param(self, node: defs.DeclClassParam) -> str:
		return node.tokens

	def on_decl_this_param(self, node: defs.DeclThisParam) -> str:
		return node.tokens

	def on_types_name(self, node: defs.TypesName) -> str:
		return self.to_domain_name_by_class(node.class_types.as_a(defs.ClassDef))

	def on_import_name(self, node: defs.ImportName) -> str:
		"""Note: @deprecated XXX ImportAsName内で利用されるだけでこのノードは展開されないためハンドラーは不要"""
		return node.tokens

	def on_import_as_name(self, node: defs.ImportAsName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		receiver_symbol = self.reflections.type_of(node.receiver).impl(refs.Object)
		receiver_is_type_ref = receiver_symbol.type_is(type)
		receiver_symbol = receiver_symbol.actualize()
		prop_symbol = receiver_symbol.prop_of(node.prop)

		spec, operator = self.analyze_relay_spec(node, receiver_symbol, receiver_is_type_ref)
		prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.ClassDef) else node.prop.domain_name
		is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
		relay_vars = {'receiver': receiver, 'operator': operator, 'prop': prop, 'is_property': is_property}
		if spec == 'cvar_relay':
			# 期待値: receiver.on().prop
			cvar_receiver = PatternParser.sub_cvar_relay(receiver)
			return self.view.render(f'{node.classification}/default', vars={**relay_vars, 'receiver': cvar_receiver})
		elif spec.startswith('cvar_to_'):
			# 期待値: receiver.raw()
			cvar_receiver = PatternParser.sub_cvar_to(receiver)
			move = spec.split('cvar_to_')[1]
			return self.view.render(f'{node.classification}/cvar_to', vars={**relay_vars, 'receiver': cvar_receiver, 'move': move})
		elif spec == '__module__':
			return self.view.render(f'{node.classification}/{spec}', vars={**relay_vars, 'module_path': receiver_symbol.types.module_path})
		elif spec == '__name__':
			return self.view.render(f'{node.classification}/{spec}', vars={**relay_vars, 'symbol': self.to_domain_name_by_class(receiver_symbol.types)})
		elif spec == '__qualname__':
			return self.view.render(f'{node.classification}/{spec}', vars=relay_vars)
		else:
			return self.view.render(f'{node.classification}/default', vars=relay_vars)

	def analyze_relay_spec(self, node: defs.Relay, receiver_symbol: IReflection, receiver_is_type_ref: bool) -> tuple[str, str]:
		def is_this_relay() -> bool:
			return node.receiver.is_a(defs.ThisRef)

		def is_on_cvar_relay() -> bool:
			return isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.relay_key

		def is_on_cvar_exchanger() -> bool:
			return node.prop.domain_name in CVars.exchanger_keys

		def is_type_relay() -> bool:
			return receiver_is_type_ref or isinstance(receiver_symbol.node, defs.Super)

		if node.prop.tokens in ['__module__', '__name__', '__qualname__']:
			return node.prop.tokens, CVars.RelayOperators.Raw.name
		elif is_this_relay():
			return 'default', CVars.RelayOperators.Address.name
		elif is_on_cvar_relay():
			cvar_key = CVars.key_from(receiver_symbol.context)
			if not CVars.is_raw_raw(cvar_key):
				return 'cvar_relay', CVars.to_operator(cvar_key).name
		elif is_on_cvar_exchanger():
			cvar_key = CVars.key_from(receiver_symbol)
			move = CVars.to_move(cvar_key, node.prop.domain_name)
			return f'cvar_to_{move.name}', CVars.to_operator(cvar_key).name
		elif is_type_relay():
			return 'default', CVars.RelayOperators.Static.name

		return 'default', CVars.RelayOperators.Raw.name

	def on_var(self, node: defs.Var) -> str:
		symbol = self.reflections.type_of(node).impl(refs.Object).actualize('type')
		if isinstance(symbol.decl, defs.ClassDef):
			return self.to_domain_name_by_class(symbol.types)
		else:
			return node.tokens

	def on_class_ref(self, node: defs.ClassRef) -> str:
		symbol = self.reflections.type_of(node).impl(refs.Object).actualize('self', 'type')
		return self.to_domain_name(symbol)

	def on_this_ref(self, node: defs.ThisRef) -> str:
		return 'this'

	def on_indexer(self, node: defs.Indexer, receiver: str, keys: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block)
		spec, context = self.analyze_indexer_spec(node)
		vars = {'receiver': receiver, 'keys': keys, 'is_statement': is_statement}
		if spec == 'slice_string':
			return self.view.render(f'{node.classification}/{spec}', vars=vars)
		elif spec == 'slice_array':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'var_type': var_type})
		elif spec == 'cvar_relay':
			# 期待値: receiver.on()[key]
			cvar_receiver = PatternParser.sub_cvar_relay(receiver)
			return self.view.render(f'{node.classification}/default', vars={**vars, 'receiver': cvar_receiver, 'key': keys[0]})
		elif spec == 'cvar':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'var_type': var_type})
		elif spec == 'class':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'var_type': var_type})
		elif spec == 'tuple':
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'receiver': receiver, 'key': keys[0]})
		else:
			return self.view.render(f'{node.classification}/default', vars={**vars, 'receiver': receiver, 'key': keys[0]})

	def analyze_indexer_spec(self, node: defs.Indexer) -> tuple[str, IReflection | None]:
		def is_on_cvar_relay() -> bool:
			return isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.relay_key

		def is_cvar() -> bool:
			return node.receiver.domain_name in CVars.keys()

		if node.sliced:
			receiver_symbol = self.reflections.type_of(node.receiver).impl(refs.Object).actualize()
			spec = 'slice_string' if receiver_symbol.type_is(str) else 'slice_array'
			return spec, receiver_symbol
		elif is_on_cvar_relay():
			receiver_symbol = self.reflections.type_of(node.receiver).impl(refs.Object).actualize()
			cvar_key = CVars.key_from(receiver_symbol.context)
			if not CVars.is_raw_raw(cvar_key):
				return 'cvar_relay', None
		elif is_cvar():
			symbol = self.reflections.type_of(node)
			return 'cvar', symbol.impl(refs.Object).actualize()
		else:
			receiver_symbol = self.reflections.type_of(node.receiver).impl(refs.Object).actualize()
			if receiver_symbol.type_is(tuple):
				return 'tuple', None

			symbol = self.reflections.type_of(node).impl(refs.Object)
			if symbol.type_is(type):
				return 'class', symbol.actualize()

		return 'otherwise', None

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: str) -> str:
		prop_symbol = self.reflections.type_of(node.receiver).impl(refs.Object).prop_of(node.prop)
		type_name = self.to_domain_name_by_class(prop_symbol.types)
		return self.view.render(node.classification, vars={'receiver': receiver, 'type_name': type_name})

	def on_var_of_type(self, node: defs.VarOfType) -> str:
		symbol = self.reflections.type_of(node)
		# ノードが戻り値の型であり、且つSelfの場合、所属クラスのシンボルに変換 FIXME 場当たり的、且つ不完全なため修正を検討
		if isinstance(node.parent, (defs.Method, defs.ClassMethod)) and isinstance(symbol.types, defs.TemplateClass) and symbol.types.domain_name == Self.__name__:
			symbol = self.reflections.resolve(node.parent.class_types)

		type_name = self.to_domain_name_by_class(symbol.types)
		if isinstance(symbol.types, defs.TemplateClass):
			return self.view.render(f'{node.classification}/template', vars={'type_name': type_name, 'definition_type': symbol.types.definition_type.tokens})
		else:
			return self.view.render(f'{node.classification}/default', vars={'type_name': type_name})

	def on_list_type(self, node: defs.ListType, type_name: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_callable_type(self, node: defs.CallableType, type_name: str, parameters: list[str], return_type: str) -> str:
		"""
		Note:
			### PluckMethodのシグネチャー
			* `Callable[[T, *T_Args], None]`
		"""
		spec = 'default'
		if len(parameters) >= 2:
			second_type = self.reflections.type_of(node.parameters[1])
			if isinstance(second_type.types, defs.TemplateClass) and second_type.types.definition_type.type_name.tokens == TypeVarTuple.__name__:
				spec = 'pluck_method'

		return self.view.render(f'{node.classification}/{spec}', vars={'type_name': type_name, 'parameters': parameters, 'return_type': return_type})

	def on_custom_type(self, node: defs.CustomType, type_name: str, template_types: list[str]) -> str:
		# XXX @see semantics.reflection.helper.naming.ClassShorthandNaming.domain_name
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
		is_addr = isinstance(var_type_node, defs.CustomType) and CVars.is_addr(var_type_node.domain_name)
		if not is_addr:
			raise LogicError(f'Unexpected UnionType. with not address. symbol: {node.fullyname}, var_type: {var_type_node}')

		return or_types[var_type_index]

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block)
		spec, context = self.analyze_func_call_spec(node)
		func_call_vars = {'calls': calls, 'arguments': arguments, 'is_statement': is_statement}
		if spec == 'c_include':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_macro':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_pragma':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_func':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == PythonClassOperations.copy_constructor:
			# 期待値: 'receiver.__py_copy__'
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == 'generic_call':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'cast_char':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'cast_enum':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/cast_bin_to_bin', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_list':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'cast_bin_to_bin':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_bin_to_str':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_str_to_bin':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_str_to_str':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'len':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'print':
			# XXX 愚直に対応すると実引数の型推論のコストが高く、その割に出力メッセージの柔軟性が下がりメリットが薄いため、関数名の置き換えのみを行う簡易的な対応とする
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'str_format':
			is_literal = node.calls.as_a(defs.Relay).receiver.is_a(defs.String)
			receiver, operator = PatternParser.break_relay(calls)
			to_tags = {int.__name__: '%d', float.__name__: '%f', bool.__name__: '%d', str.__name__: '%s', CP.__name__: '%p'}
			formatters: list[dict[str, Any]] = []
			for argument in node.arguments:
				arg_symbol = self.reflections.type_of(argument)
				formatters.append({'label': argument.label.tokens, 'tag': to_tags.get(arg_symbol.types.domain_name, '%s'), 'var_type': arg_symbol.types.domain_name, 'is_literal': argument.value.is_a(defs.Literal)})

			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'is_literal': is_literal, 'formatters': formatters})
		elif spec == 'list_pop':
			# 期待値: 'receiver.pop'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'list_insert':
			# 期待値: 'receiver.insert'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == 'list_extend':
			# 期待値: 'receiver.extend'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == 'dict_pop':
			# 期待値: 'receiver.pop'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'dict_keys':
			# 期待値: 'receiver.keys'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'dict_values':
			# 期待値: 'receiver.values'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'cvar_copy':
			# 期待値: cref_to.copy(cref_via)
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == 'cvar_new_p':
			# 期待値: CP.new(A(a, b, c))
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'cvar_new_sp_list':
			var_type = self.to_accessible_name(cast(IReflection, context))
			# 期待値1: CSP.new([1, 2, 3])
			initializer = arguments[0]
			# 期待値2: CSP.new(list[int]())
			if isinstance(node.arguments[0].value, defs.FuncCall) and len(node.arguments[0].value.arguments) == 0:
				initializer = ''
			# 期待値3: ソース: CSP.new([0] * size) -> トランスパイル後: std::shared_ptr<std::vector<int>>(new std::vector<int>(size, 0))
			# 期待値4: ソース: CSP.new(list[int]() * size) -> トランスパイル後: std::shared_ptr<std::vector<int>>(new std::vector<int>(size))
			elif isinstance(node.arguments[0].value, defs.Term):
				initializer = BlockParser.parse_bracket(initializer)[0][1:-1]

			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		elif spec == 'cvar_new_sp':
			var_type = self.to_accessible_name(cast(IReflection, context))
			# 期待値: CSP.new(A(a, b, c))
			initializer = PatternParser.pluck_cvar_new_argument(arguments[0])
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		elif spec == 'cvar_sp_empty':
			# 期待値: CSP[A].empty()
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec.startswith('cvar_to_'):
			cvar_type = spec.split('cvar_to_')[1]
			return self.view.render(f'{node.classification}/cvar_to', vars={**func_call_vars, 'cvar_type': cvar_type})
		else:
			return self.view.render(f'{node.classification}/default', vars=func_call_vars)

	def analyze_func_call_spec(self, node: defs.FuncCall) -> tuple[str, IReflection | None]:
		"""
		Note:
			XXX callsは別名になる可能性があるため、ノードから取得したcallsを使用する
		"""
		if isinstance(node.calls, defs.Var):
			calls = node.calls.tokens
			if calls == c_pragma.__name__:
				return 'c_pragma', None
			elif calls == c_include.__name__:
				return 'c_include', None
			elif calls == c_macro.__name__:
				return 'c_macro', None
			elif calls in [c_func_addr.__name__, c_func_ref.__name__]:
				return 'c_func', None
			elif calls == len.__name__:
				return 'len', self.reflections.type_of(node.arguments[0])
			elif calls == print.__name__:
				return 'print', None
			elif calls == 'char':
				return 'cast_char', None
			elif calls == 'list':
				return 'cast_list', None
			elif calls in ['int', 'float', 'bool', 'str']:
				casted_types = {'int': int, 'float': float, 'bool': bool, 'str': str}
				to_type = casted_types[calls]
				from_raw = self.reflections.type_of(node.arguments[0]).impl(refs.Object)
				to_raw = self.reflections.from_standard(to_type).impl(refs.Object)
				if from_raw.type_is(str) and to_raw.type_is(str):
					return 'cast_str_to_str', to_raw
				elif from_raw.type_is(str):
					return 'cast_str_to_bin', to_raw
				elif to_type is str:
					return 'cast_bin_to_str', from_raw
				else:
					return 'cast_bin_to_bin', to_raw
			elif calls in CVars.keys():
				return f'cvar_to_{calls}', None
		elif isinstance(node.calls, defs.Relay):
			prop = node.calls.prop.tokens
			if prop in ['pop', 'insert', 'extend', 'keys', 'values']:
				context = self.reflections.type_of(node.calls).context.impl(refs.Object)
				if prop in ['pop', 'insert', 'extend'] and context.type_is(list):
					return f'list_{prop}', context.attrs[0]
				elif prop in ['pop', 'keys', 'values'] and context.type_is(dict):
					key_attr, value_attr = context.attrs
					attr_indexs = {'pop': value_attr, 'keys': key_attr, 'values': value_attr}
					return f'dict_{prop}', attr_indexs[prop]
			elif prop == PythonClassOperations.copy_constructor:
				return prop, None
			elif prop == 'format':
				if node.calls.receiver.is_a(defs.String):
					return 'str_format', None
				elif self.reflections.type_of(node.calls).context.impl(refs.Object).type_is(str):
					return 'str_format', None
			elif prop == CVars.copy_key:
				receiver_raw = self.reflections.type_of(node.calls.receiver)
				cvar_key = CVars.key_from(receiver_raw)
				if CVars.is_raw_ref(cvar_key):
					return 'cvar_copy', None
			elif prop == CVars.empty_key:
				if isinstance(node.calls.receiver, defs.Indexer) and CVars.is_addr_sp(node.calls.receiver.receiver.domain_name):
					# 期待値: CSP[A] | None
					context = self.reflections.type_of(node).attrs[0].attrs[0]
					return 'cvar_sp_empty', context
			elif prop == CVars.allocator_key:
				if isinstance(node.calls.receiver, defs.Var) and CVars.is_addr_p(node.calls.receiver.domain_name):
					return 'cvar_new_p', None
				elif isinstance(node.calls.receiver, defs.Var) and CVars.is_addr_sp(node.calls.receiver.domain_name):
					new_type_raw = self.reflections.type_of(node.arguments[0])
					spec = 'cvar_new_sp_list' if new_type_raw.impl(refs.Object).type_is(list) else 'cvar_new_sp'
					return spec, new_type_raw

		if isinstance(node.calls, (defs.Relay, defs.Var)):
			if len(node.arguments) > 0 and node.arguments[0].value.is_a(defs.Reference):
				primary_arg_raw = self.reflections.type_of(node.arguments[0])
				if primary_arg_raw.impl(refs.Object).type_is(type):
					return 'generic_call', None

			raw = self.reflections.type_of(node.calls).impl(refs.Object).actualize()
			if raw.types.is_a(defs.Enum):
				return 'cast_enum', raw

		return 'otherwise', None

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		parent_symbol = self.reflections.type_of(node)
		return self.to_accessible_name(parent_symbol)

	def on_for_in(self, node: defs.ForIn, iterates: str) -> str:
		return iterates

	def on_comp_for(self, node: defs.CompFor, symbols: list[str], for_in: str) -> str:
		"""Note: XXX range/enumerateは効率・可読性共に非常に悪いため非サポート"""
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens in [range.__name__, enumerate.__name__]:
			raise LogicError(f'Operation not allowed. "{node.iterates.calls.tokens}" is not supported. node: {node}')

		for_in_symbol = self.reflections.type_of(node.for_in)
		# FIXME is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		is_const = CVars.is_const(CVars.key_from(for_in_symbol))
		is_addr_p = CVars.is_addr(CVars.key_from(for_in_symbol))

		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) and node.iterates.calls.prop.tokens == dict.items.__name__:
			# 期待値: 'iterates.items()'
			iterates = PatternParser.pluck_dict_items_receiver(for_in)
			# XXX 参照の変換方法が場当たり的で一貫性が無い。包括的な対応を検討
			iterates = f'*({iterates})' if for_in.endswith('->items()') else iterates
			return self.view.render(f'comp/{node.classification}', vars={'symbols': symbols, 'iterates': iterates, 'is_const': is_const, 'is_addr_p': is_addr_p})
		else:
			return self.view.render(f'comp/{node.classification}', vars={'symbols': symbols, 'iterates': for_in, 'is_const': is_const, 'is_addr_p': is_addr_p})

	def on_list_comp(self, node: defs.ListComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.reflections.type_of(node.projection)
		projection_type = self.to_accessible_name(projection_type_raw)
		comp_vars = {'projection': projection, 'comp_for': fors[0], 'condition': condition, 'projection_types': [projection_type]}
		return self.view.render(f'comp/{node.classification}', vars=comp_vars)

	def on_dict_comp(self, node: defs.DictComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.reflections.type_of(node.projection)
		projection_type_key = self.to_accessible_name(projection_type_raw.attrs[0])
		projection_type_value = self.to_accessible_name(projection_type_raw.attrs[1])
		projection_pair_node = node.projection.as_a(defs.Pair)
		# XXX 再帰的なトランスパイルでkey/valueを解決
		projection_key = self.transpile(projection_pair_node.first)
		projection_value = self.transpile(projection_pair_node.second)
		comp_vars = {'projection_key': projection_key, 'projection_value': projection_value, 'comp_for': fors[0], 'condition': condition, 'projection_types': [projection_type_key, projection_type_value]}
		return self.view.render(f'comp/{node.classification}', vars=comp_vars)

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

		list_is_primary = primary_raw.impl(refs.Object).type_is(list)
		list_is_secondary = secondary_raws[0].impl(refs.Object).type_is(list)
		if list_is_primary != list_is_secondary and operators[0] == '*':
			default_raw, default = (primary_raw, primary) if list_is_primary else (secondary_raws[0], secondaries[0])
			size_raw, size = (secondary_raws[0], secondaries[0]) if list_is_primary else (primary_raw, primary)
			return self.proc_binary_operator_fill_list(node, default_raw, size_raw, default, size)
		else:
			return self.proc_binary_operator_expression(node, primary_raw, secondary_raws, primary, operators, secondaries)

	def proc_binary_operator_fill_list(self, node: defs.BinaryOperator, default_raw: IReflection, size_raw: IReflection, default: str, size: str) -> str:
		value_type = self.to_accessible_name(default_raw.attrs[0])
		default_is_list = default_raw.node.is_a(defs.List)
		return self.view.render('binary_operator/fill_list', vars={'value_type': value_type, 'default': default, 'size': size, 'default_is_list': default_is_list})

	def proc_binary_operator_expression(self, node: defs.BinaryOperator, left_raw: IReflection, right_raws: list[IReflection], left: str, operators: list[str], rights: list[str]) -> str:
		primary = left
		for index, right_raw in enumerate(right_raws):
			operator = operators[index]
			secondary = rights[index]
			if operator in ['in', 'not.in']:
				primary = self.view.render('binary_operator/in', vars={'left': primary, 'operator': operator, 'right': secondary, 'right_is_dict': right_raw.impl(refs.Object).type_is(dict)})
			else:
				primary = self.view.render('binary_operator/default', vars={'left': primary, 'operator': operator, 'right': secondary, 'left_var_type': self.to_domain_name(left_raw)})

		return primary

	def on_tenary_operator(self, node: defs.TenaryOperator, primary: str, condition: str, secondary: str) -> str:
		return self.view.render(node.classification, vars={'primary': primary, 'condition': condition, 'secondary': secondary})

	# Literal

	def on_string(self, node: defs.String) -> str:
		return f'"{node.tokens[1:-1]}"'

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

	def on_tuple(self, node: defs.Tuple, values: list[str]) -> str:
		return self.view.render(node.classification, vars={'values': values})

	def on_null(self, node: defs.Null) -> str:
		return 'nullptr'

	# Expression

	def on_group(self, node: defs.Group, expression: str) -> str:
		return f'({expression})'

	def on_expander(self, node: defs.Expander, expression: str) -> str:
		raise NotSupportedError(f'Denied list expand expression. node: {node}')

	# Terminal

	def on_terminal(self, node: Node) -> str:
		return node.tokens

	# Fallback

	def on_fallback(self, node: Node) -> str:
		return node.tokens


class PatternParser:
	"""正規表現によるパターン解析ユーティリティー

	Note:
		これらは正規表現を用いないで済む方法へ修正を検討
	"""

	# 期待値: path.to->prop -> ('path.to', '->')
	RelayPattern = re.compile(r'(.+)(->|::|\.)\w+')
	# 期待値: path.to.calls(arguments...) -> 'arguments...'
	FuncCallArgumentsPattern = re.compile(r'\w+\((.+)\)')
	# 期待値: path.to.items() -> 'path.to'
	DictItemsPattern = re.compile(r'(.+)(->|\.)\w+\(\)')
	# 期待値: Class::__init__(arguments...); -> 'arguments...'
	SuperArgumentsPattern = re.compile(r'\(([^)]*)\);$')
	# 期待値: path.to = right; -> 'right'
	AssignRightPattern = re.compile(r'=\s*([^;]+);$')
	# 期待値: path.to[key] -> ('path.to', 'key') XXX 複雑な式に耐えられないため修正を検討
	IndexerPattern = re.compile(r'(.+)\[(.+)\]')
	# 期待値: Class(arguments...) -> 'arguments...'
	CVarNewArgumentPattern = re.compile(r'^[^(]+\((.*)\)$')
	# 期待値: path.on()->to -> 'path.to'
	CVarRelaySubPattern = re.compile(rf'(->|::|\.){CVars.relay_key}\(\)$')
	# 期待値: path.to.raw() -> 'path.to'
	CVarToSubPattern = re.compile(rf'(->|::|\.)({"|".join(CVars.exchanger_keys)})\(\)$')

	@classmethod
	def break_relay(cls, relay: str) -> tuple[str, str]:
		"""リレーからレシーバーとオペレーターに分解

		Args:
			relay (str): 文字列
		Returns:
			tuple[str, str]: (レシーバー, オペレーター)
		"""
		return cast(re.Match, cls.RelayPattern.fullmatch(relay)).group(1, 2)

	@classmethod
	def pluck_func_call_arguments(cls, func_call: str) -> str:
		"""関数コールから引数リストの部分を抜き出す

		Args:
			func_call (str): 文字列
		Returns:
			str: 引数リスト
		"""
		return cast(re.Match, cls.FuncCallArgumentsPattern.fullmatch(func_call))[1]

	@classmethod
	def pluck_dict_items_receiver(cls, func_call: str) -> str:
		"""関数コール(dict.items)からレシーバーの部分を抜き出す

		Args:
			func_call (str): 文字列
		Returns:
			str: レシーバー
		"""
		return cast(re.Match, cls.DictItemsPattern.fullmatch(func_call))[1]

	@classmethod
	def pluck_super_arguments(cls, func_call: str) -> str:
		"""関数コール(super)から引数リストの部分を抜き出す

		Args:
			func_call (str): 文字列
		Returns:
			str: 引数リスト
		"""
		return cast(re.Match, cls.SuperArgumentsPattern.search(func_call))[1]

	@classmethod
	def pluck_assign_right(cls, assign: str) -> str:
		"""代入式から右辺の部分を抜き出す

		Args:
			assign (str): 文字列
		Returns:
			str: 右辺
		"""
		matches = cls.AssignRightPattern.search(assign)
		return matches[1] if matches else ''

	@classmethod
	def break_indexer(cls, indexer: str) -> tuple[str, str]:
		"""インデクサーからレシーバーとキーに分解

		Args:
			assign (str): 文字列
		Returns:
			tuple[str, str]: (レシーバー, キー)
		"""
		return cast(re.Match, cls.IndexerPattern.fullmatch(indexer)).group(1, 2)

	@classmethod
	def pluck_cvar_new_argument(cls, argument: str) -> str:
		"""C++型変数のメモリー生成関数コールから引数の部分を抜き出す

		Args:
			argument (str): 文字列
		Returns:
			str: 引数
		"""
		return cast(re.Match, cls.CVarNewArgumentPattern.fullmatch(argument))[1]

	@classmethod
	def sub_cvar_relay(cls, receiver: str) -> str:
		"""C++型変数のリレープロクシーを削除する

		Args:
			receiver (str): 文字列
		Returns:
			str: 引数
		"""
		return cls.CVarRelaySubPattern.sub('', receiver)

	@classmethod
	def sub_cvar_to(cls, receiver: str) -> str:
		"""C++型変数の型変換プロクシーを削除する

		Args:
			receiver (str): 文字列
		Returns:
			str: 引数
		"""
		return cls.CVarToSubPattern.sub('', receiver)
