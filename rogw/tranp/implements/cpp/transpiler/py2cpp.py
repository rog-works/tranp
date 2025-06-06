from collections.abc import Callable
import re
from typing import Any, ClassVar, Protocol, Self, TypeVarTuple, cast

from rogw.tranp.compatible.cpp.function import c_func_invoke, c_func_ref
from rogw.tranp.compatible.cpp.object import CP
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma
from rogw.tranp.compatible.python.embed import Embed
from rogw.tranp.compatible.python.types import Union
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory, TranspilerMeta
from rogw.tranp.data.version import Versions
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn, import_dsn
from rogw.tranp.errors import LogicError
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.annotation import duck_typed, implements, injectable
from rogw.tranp.lang.defer import Defer
from rogw.tranp.lang.eventemitter import Callback, Observable
from rogw.tranp.lang.module import to_fullyname
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
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.render import Renderer


class Py2Cpp(ITranspiler):
	"""Python -> C++のトランスパイラー"""

	@injectable
	def __init__(self, reflections: Reflections, render: Renderer, i18n: I18n, module_meta_factory: ModuleMetaFactory, options: TranspilerOptions) -> None:
		"""インスタンスを生成

		Args:
			reflections: シンボルリゾルバー @inject
			render: ソースレンダー @inject
			i18n: 国際化対応モジュール @inject
			module_meta_factory: モジュールのメタ情報ファクトリー @inject
			options: 実行オプション @inject
		"""
		self.reflections = reflections
		self.view = render
		self.i18n = i18n
		self.module_meta_factory = module_meta_factory
		self.include_dirs = self.__make_include_dirs(options)
		self.__procedure = self.__make_procedure(options)

	def __make_include_dirs(self, options: TranspilerOptions) -> dict[str, str]:
		"""インクルードディレクトリー一覧

		Args:
			dict[str, str]: インクルードディレクトリー一覧
		"""
		include_dirs: dict[str, str] = {}
		for include_dir in cast(list[str], options.env.get('include_dirs', [])):
			elems = include_dir.split(':') if include_dir.count(':') == 1 else [include_dir]
			include_dirs[elems[0]] = elems[1] if len(elems) == 2 else ''

		return include_dirs

	def __make_procedure(self, options: TranspilerOptions) -> Procedure[str]:
		"""プロシージャーを生成

		Args:
			options: 実行オプション
		Returns:
			プロシージャー
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
			action: アクション名
			callback: ハンドラー
		"""
		self.__procedure.on(action, callback)

	@duck_typed(Observable)
	def off(self, action: str, callback: Callback[str]) -> None:
		"""イベントハンドラーを解除

		Args:
			action: アクション名
			callback: ハンドラー
		"""
		self.__procedure.off(action, callback)

	@property
	@implements
	def meta(self) -> TranspilerMeta:
		"""Returns: トランスパイラーのメタ情報"""
		return {'version': Versions.py2cpp, 'module': to_fullyname(Py2Cpp)}

	@implements
	def transpile(self, root: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			root: 起点のノード
		Returns:
			トランスパイル後のソースコード
		"""
		return self.__procedure.exec(root)

	def to_accessible_name(self, raw: IReflection) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得 (主にMoveAssignで利用)

		Args:
			raw: シンボル
		Returns:
			名前空間上の参照名
		Note:
			```
			### 生成例
			'Class' -> 'NS::Class'
			'dict<A, B>' -> 'dict<NS::A, NS::B>'
			'CP<A>' -> 'NS::A*'
			```
		"""
		actual_raw = raw.impl(refs.Object).actualize('nullable')
		var_type = ClassDomainNaming.accessible_name(actual_raw.types, alias_handler=self.i18n.t)
		attr_types: list[str] = [self.to_accessible_name(attr) for attr in actual_raw.attrs]
		if actual_raw.types.is_a(defs.Method):
			# FIXME アノテーションを考慮しておらず場当たり的な対応
			param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attr_types[1:-1]]
			var_type = f'{attr_types[-1]}({DSN.join(*DSN.elements(var_type)[:-1])}::*)({", ".join(param_types)})'
		elif actual_raw.types.is_a(defs.ClassMethod):
			param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attr_types[1:-1]]
			var_type = f'{attr_types[-1]}(*)({", ".join(param_types)})'
		elif actual_raw.types.is_a(defs.Function):
			param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attr_types[:-1]]
			var_type = f'{attr_types[-1]}(*)({", ".join(param_types)})'
		elif actual_raw.type_is(Callable):
			param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attr_types[:-1]]
			var_type = f'{var_type}<{attr_types[-1]}({", ".join(param_types)})>'
		elif not actual_raw.types.is_a(defs.AltClass) and len(attr_types) > 0:
			var_type = f'{var_type}<{", ".join(attr_types)}>'
		elif actual_raw.types.is_a(defs.AltClass) and not CVars.is_entity(CVars.key_from(actual_raw.attrs[0])):
			# XXX C++型変数のAltClassの特殊化であり、一般解に程遠いため修正を検討
			var_type = f'{var_type}<{", ".join([self.to_accessible_name(attr) for attr in actual_raw.attrs[0].attrs])}>'

		var_type = self.view.render('type_py2cpp', vars={'var_type': var_type})
		return DSN.join(*DSN.elements(var_type), delimiter='::')

	def to_domain_name(self, var_type_raw: IReflection) -> str:
		"""明示された型からドメイン名を取得 (主にAnnoAssignで利用)

		Args:
			var_type_raw: シンボル
		Returns:
			ドメイン名
		Note:
			```
			### 生成例
			'Union<CP<Class>, None>' -> 'Class<CP>'
			```
		"""
		actual_type_raw = var_type_raw.impl(refs.Object).actualize('nullable')
		return ClassShorthandNaming.domain_name(actual_type_raw, alias_handler=self.i18n.t)

	def to_domain_name_by_class(self, types: defs.ClassDef) -> str:
		"""明示された型からドメイン名を取得

		Args:
			types: クラス宣言ノード
		Returns:
			型の参照名
		"""
		return ClassDomainNaming.domain_name(types, alias_handler=self.i18n.t)

	def to_prop_name(self, prop_raw: IReflection) -> str:
		"""プロパティーの名前を取得

		Args:
			prop_raw: プロパティー
		Returns:
			プロパティー名
		"""
		return self.to_prop_name_by_decl(prop_raw.node.one_of(*defs.DeclAllTs))

	def to_prop_name_by_decl(self, decl: defs.DeclAll) -> str:
		"""プロパティーの名前を取得

		Args:
			decl: メソッド・変数宣言ノード
		Returns:
			プロパティー名
		"""
		return self.i18n.t(alias_dsn(decl.fullyname), fallback=decl.domain_name)

	def fetch_function_template_names(self, node: defs.Function) -> list[str]:
		"""ファンクションのテンプレート型名を取得

		Args:
			node: ファンクションノード
		Returns:
			テンプレート型名リスト
		"""
		return [types.domain_name for types in self.reflections.type_of(node).impl(refs.Function).function_templates()]

	def allow_override_from_method(self, method: defs.ClassMethod | defs.Constructor | defs.Method) -> bool:
		"""仮想関数の判定

		Args:
			method: メソッド系ノード
		Returns:
			True = 仮想関数
		Note:
			C++ではClassMethodの仮想関数はないので非対応
		"""
		return len([decorator for decorator in method.decorators if decorator.path.tokens == Embed.allow_override.__qualname__]) > 0

	def allow_move_assign(self, value_raw: IReflection, declared: bool) -> bool:
		"""代入時の型推論で許容される型か判定

		Args:
			value_raw: 値のシンボル
			declared: True = 変数宣言
		Returns:
			False = 不許可
		Note:
			実質的にNullable以外のUnion型のみ不許可
		"""
		if not declared:
			return True

		if not value_raw.impl(refs.Object).type_is(Union):
			return True

		if len(value_raw.attrs) != 2:
			return False

		var_type_raw, null_type_raw = value_raw.attrs
		var_type_key = CVars.key_from(var_type_raw.impl(refs.Object).actualize())
		return CVars.is_addr(var_type_key) and null_type_raw.impl(refs.Object).type_is(None)

	def to_accessor(self, accessor: str) -> str:
		"""アクセス修飾子を翻訳

		Args:
			accessor: アクセス修飾子
		Returns:
			翻訳後のアクセス修飾子
		"""
		return self.i18n.t(ModuleDSN.full_joined(self.i18n.t(alias_dsn('lang')), 'accessor', accessor))

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		meta_header = MetaHeader(self.module_meta_factory(node.module_path), self.meta)
		return self.view.render(node.classification, vars={'statements': statements, 'meta_header': meta_header.to_header_str(), 'module_path': node.module_path})

	# Statement - compound

	def on_else_if(self, node: defs.ElseIf, condition: str, statements: list[str]) -> str:
		return self.view.render(f'if/{node.classification}', vars={'condition': condition, 'statements': statements})

	def on_else(self, node: defs.Else, statements: list[str]) -> str:
		return self.view.render(f'if/{node.classification}', vars={'statements': statements})

	def on_if(self, node: defs.If, condition: str, statements: list[str], else_ifs: list[str], else_clause: str) -> str:
		return self.view.render(f'if/{node.classification}', vars={'condition': condition, 'statements': statements, 'else_ifs': else_ifs, 'else_clause': else_clause})

	def on_while(self, node: defs.While, condition: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'statements': statements})

	def on_for(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == range.__name__:
			return self.proc_for_range(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == enumerate.__name__:
			return self.proc_for_enumerate(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) \
			and node.iterates.calls.prop.tokens in [dict.items.__name__, dict.keys.__name__, dict.values.__name__] \
			and self.reflections.type_of(node.iterates.calls.receiver).impl(refs.Object).actualize().type_is(dict):
			return self.proc_for_dict(node, symbols, for_in, statements)
		else:
			return self.proc_for_each(node, symbols, for_in, statements)

	def proc_for_range(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# 期待値: 'range(arguments...)'
		last_index = PatternParser.pluck_func_call_arguments(for_in)
		return self.view.render(f'{node.classification}/range', vars={'symbol': symbols[0], 'last_index': last_index, 'statements': statements})

	def proc_for_enumerate(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# 期待値: 'enumerate(arguments...)'
		iterates = PatternParser.pluck_func_call_arguments(for_in)
		var_type = self.to_accessible_name(self.reflections.type_of(node.for_in).attrs[1])
		return self.view.render(f'{node.classification}/enumerate', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements, 'var_type': var_type})

	def proc_for_dict(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# XXX is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		for_in_symbol = Defer.new(lambda: self.reflections.type_of(node.for_in).impl(refs.Object).actualize())
		is_const = CVars.is_const(CVars.key_from(for_in_symbol)) if len(symbols) == 1 else False
		# 期待値: 'iterates.items()'
		receiver, operator, method_name = PatternParser.break_dict_iterator(for_in)
		# XXX 参照の変換方法が場当たり的で一貫性が無い。包括的な対応を検討
		iterates = f'*({receiver})' if operator == '->' else receiver
		dict_symbols = {dict.items.__name__: symbols, dict.keys.__name__: [symbols[0], '_'], dict.values.__name__: ['_', symbols[0]]}
		return self.view.render(f'{node.classification}/dict', vars={'symbols': dict_symbols[method_name], 'iterates': iterates, 'statements': statements, 'is_const': is_const, 'is_addr_p': False})

	def proc_for_each(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# XXX is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		for_in_symbol = Defer.new(lambda: self.reflections.type_of(node.for_in).impl(refs.Object).actualize())
		is_const = CVars.is_const(CVars.key_from(for_in_symbol)) if len(symbols) == 1 else False
		is_addr_p = CVars.is_addr_p(CVars.key_from(for_in_symbol)) if len(symbols) == 1 else False
		return self.view.render(f'{node.classification}/default', vars={'symbols': symbols, 'iterates': for_in, 'statements': statements, 'is_const': is_const, 'is_addr_p': is_addr_p})

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
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		return self.view.render(f'function/{node.classification}', vars=function_vars)

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = self.fetch_function_template_names(node)
		return_type_annotation = self.transpile(node.return_type.annotation) if not isinstance(node.return_type.annotation, defs.Empty) else ''
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'return_type_annotation': return_type_annotation}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars})

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		this_vars = node.class_types.as_a(defs.Class).this_vars

		# クラスの初期化ステートメントとそれ以外を分離
		this_var_declares = [this_var.declare.one_of(*defs.DeclAssignTs) for this_var in this_vars]
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
			super_initializer['parent'] = super_initializer_statement.split('::')[-2]
			# 期待値: `Class::__init__(a, b, c);`
			super_initializer['arguments'] = PatternParser.pluck_super_arguments(super_initializer_statement)

		# メンバー変数の宣言用のデータを生成
		initializers: list[dict[str, str]] = []
		for index, this_var in enumerate(this_vars):
			# 期待値: `this->a = 1234;`
			initial_value = PatternParser.pluck_decl_right(initializer_statements[index])
			initializer = {'symbol': self.i18n.t(alias_dsn(this_var.fullyname), this_var.domain_name), 'value': initial_value}
			initializers.append(initializer)

		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = self.fetch_function_template_names(node)
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': normal_statements, 'template_types': template_types}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'allow_override': self.allow_override_from_method(node)}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = self.fetch_function_template_names(node)
		return_type_annotation = self.transpile(node.return_type.annotation) if not isinstance(node.return_type.annotation, defs.Empty) else ''
		_symbol = ClassOperationMaps.operators.get(symbol, symbol)
		function_vars = {'symbol': _symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'is_property': node.is_property, 'allow_override': self.allow_override_from_method(node), 'return_type_annotation': return_type_annotation}
		spec = ClassOperationMaps.ctors.get(symbol, node.classification)
		return self.view.render(f'function/{spec}', vars={**function_vars, **method_vars})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'statements': statements}
		return self.view.render(f'function/{node.classification}', vars=function_vars)

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		if len(inherits) == 1 and inherits[0] == Protocol.__name__:
			return self.proc_class_protocol(node, symbol, decorators, inherits, template_types, comment, statements)
		else:
			return self.proc_class(node, symbol, decorators, inherits, template_types, comment, statements)

	def proc_class_protocol(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		class_vars = {'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'template_types': template_types, 'comment': comment, 'statements': statements, 'module_path': node.module_path}
		return self.view.render(f'{node.classification}/protocol', vars=class_vars)

	def proc_class(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		# XXX 構造体の判定
		is_struct = len([decorator for decorator in decorators if decorator.startswith(Embed.struct.__qualname__)])

		# XXX クラス配下の変数宣言とそれ以外のステートメントを分離
		a_statements = statements.copy()
		class_var_statements: list[tuple[int, str]] = []
		this_var_statements: list[tuple[int, str]] = []
		for index, statement in enumerate(node.statements):
			if isinstance(statement, defs.AnnoAssign):
				if isinstance(statement.receiver, defs.DeclClassVar):
					class_var_statements.append((index, statements[index]))
				elif isinstance(statement.receiver, defs.DeclThisVarForward):
					this_var_statements.append((index, statements[index]))

		# XXX メンバー変数の展開方法を検討
		for index, class_var_statement in class_var_statements:
			class_var_name = PatternParser.pluck_class_var_name(class_var_statement)
			class_var_vars = {'accessor': self.to_accessor(defs.to_accessor(class_var_name)), 'decl_class_var': class_var_statement}
			a_statements[index] = self.view.render(f'{node.classification}/_decl_class_var', vars=class_var_vars)

		for var_index, decl_this_var_item in enumerate(node.decl_this_vars.items()):
			index, this_var_statement = this_var_statements[var_index]
			this_var_name, decl_this_var = decl_this_var_item
			this_var_annotation = self.transpile(decl_this_var.var_type.annotation) if not isinstance(decl_this_var.var_type.annotation, defs.Empty) else ''
			this_var_vars = {'accessor': self.to_accessor(defs.to_accessor(this_var_name)), 'decl_this_var': this_var_statement, 'annotation': this_var_annotation}
			a_statements[index] = self.view.render(f'{node.classification}/_decl_this_var', vars=this_var_vars)

		accessor = self.to_accessor(node.accessor) if node.is_internal else ''

		class_vars = {'accessor': accessor, 'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'template_types': template_types, 'comment': comment, 'statements': a_statements, 'module_path': node.module_path, 'is_struct': is_struct}
		return self.view.render(f'{node.classification}/class', vars=class_vars)

	def on_enum(self, node: defs.Enum, symbol: str, decorators: list[str], inherits: list[str], template_types: list[str], comment: str, statements: list[str]) -> str:
		add_vars = {}
		if not node.parent.is_a(defs.Entrypoint):
			add_vars = {'accessor': self.to_accessor(node.accessor)}

		accessor = self.to_accessor(node.accessor) if node.is_internal else ''

		return self.view.render(f'class/{node.classification}', vars={'accessor': accessor, 'symbol': symbol, 'decorators': decorators, 'comment': comment, 'statements': statements, 'module_path': node.module_path, **add_vars})

	def on_alt_class(self, node: defs.AltClass, symbol: str, actual_type: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'actual_type': actual_type})

	def on_template_class(self, node: defs.TemplateClass, symbol: str) -> str:
		return f'// template<typename {symbol}>'

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		annotation = self.transpile(node.var_type.annotation) if isinstance(node.var_type, defs.Type) and not isinstance(node.var_type.annotation, defs.Empty) else ''
		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value, 'annotation': annotation})

	def on_decorator(self, node: defs.Decorator, path: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'path': path, 'arguments': arguments})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		if len(receivers) == 1:
			return self.proc_move_assign_single(node, receivers[0], value)
		else:
			return self.proc_move_assign_destruction(node, receivers, value)

	def proc_move_assign_single(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		receiver_is_dict = isinstance(node.receivers[0], defs.Indexer) and self.reflections.type_of(node.receivers[0].receiver).impl(refs.Object).type_is(dict)
		if receiver_is_dict:
			return self.view.render(f'assign/{node.classification}_dict', vars={'receiver': receiver, 'value': value})

		receiver_raw = self.reflections.type_of(node.receivers[0])
		value_raw = self.reflections.type_of(node.value)
		declared = receiver_raw.decl.declare == node
		if not self.allow_move_assign(value_raw, declared):
			raise LogicError(f'Not allowed assign type. node: {node}, symbol: {value_raw}')

		var_type = self.to_accessible_name(value_raw)
		assign_vars = {'receiver': receiver, 'var_type': var_type, 'value': value}
		if not declared:
			return self.view.render(f'assign/{node.classification}', vars=assign_vars)
		elif isinstance(node.value, defs.FuncCall) and node.value.calls.tokens == Embed.static.__qualname__:
			return self.view.render(f'assign/{node.classification}_declare', vars={**assign_vars, 'is_static': True})
		elif isinstance(node.value, defs.FuncCall) and value.startswith(f'{var_type}('):
			return self.view.render(f'assign/{node.classification}_declare', vars={**assign_vars, 'is_initializer': True})
		else:
			return self.view.render(f'assign/{node.classification}_declare', vars=assign_vars)

	def proc_move_assign_destruction(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		"""Note: C++で分割代入できるのはtuple/pairのみ。Pythonではいずれもtupleのため、tuple以外は非対応"""
		value_raw = self.reflections.type_of(node.value).impl(refs.Object).actualize()
		if not value_raw.type_is(tuple):
			raise LogicError(f'Not allowed destruction assign. value must be a tuple. node: {node}')

		return self.view.render(f'assign/{node.classification}_destruction', vars={'receivers': receivers, 'value': value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		annotation = self.transpile(node.var_type.annotation) if not isinstance(node.var_type.annotation, defs.Empty) else ''
		assign_vars = {'receiver': receiver, 'var_type': var_type, 'value': value, 'annotation': annotation}
		if isinstance(node.value, defs.FuncCall) and value.startswith(f'{var_type}('):
			return self.view.render(f'assign/{node.classification}', vars={**assign_vars, 'is_initializer': True})
		else:
			return self.view.render(f'assign/{node.classification}', vars=assign_vars)

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

	def on_assert(self, node: defs.Assert, condition: str, assert_body: str) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'assert_body': assert_body})

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(node.classification, vars={'throws': throws, 'via': via, 'is_new': node.throws.is_a(defs.FuncCall)})

	def on_pass(self, node: defs.Pass) -> str:
		# XXX statementsのスタック数が合わなくなるため出力
		return ''

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_comment(self, node: defs.Comment) -> str:
		return self.view.render(node.classification, vars={'text': node.text})

	def on_import(self, node: defs.Import, symbols: list[str]) -> str:
		"""
		Note:
			```
			### インクルードパスの生成方法に関して
			1. 翻訳データにインポート置換用のDSNを登録 @see rogw.tranp.dsn.translation.import_dsn
			2. 環境変数のインポートディレクトリーを元に生成 @see example/config.yml
			```
		"""
		module_path = node.import_path.tokens
		text = self.i18n.t(import_dsn(module_path), '')
		if text:
			return text

		import_dir = ''
		replace_dir = ''
		for in_import, in_replace in self.include_dirs.items():
			if len(import_dir) < len(in_import) and module_path.startswith(in_import.replace('/', '.')):
				import_dir = in_import
				replace_dir = in_replace

		return self.view.render(node.classification, vars={'module_path': module_path, 'import_dir': import_dir, 'replace_dir': replace_dir, 'symbols': symbols})

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
		org_receiver_symbol = Defer.new(lambda: self.reflections.type_of(node.receiver).impl(refs.Object))
		receiver_symbol = Defer.new(lambda: org_receiver_symbol.actualize())
		prop_symbol = Defer.new(lambda: receiver_symbol.prop_of(node.prop))
		if self.is_relay_literalizer(node, receiver_symbol):
			org_prop = node.prop.domain_name
			if org_prop == '__name__':
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'literal': self.to_domain_name_by_class(receiver_symbol.types)})
			elif org_prop == '__module__':
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'literal': receiver_symbol.types.module_path})
			elif org_prop == 'name':
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'literal': node.receiver.as_a(defs.Relay).prop.tokens})
			elif org_prop == 'value':
				var_name = DSN.right(node.receiver.domain_name, 1)
				var_literal = receiver_symbol.types.as_a(defs.Enum).var_value_of(var_name)
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': var_literal.literal_identifier, 'literal': var_literal.as_string if isinstance(var_literal, defs.String) else var_literal.tokens})
			else:
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'literal': receiver})
		elif self.is_relay_this(node):
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Address.name, 'prop': prop, 'is_property': is_property})
		elif self.is_relay_cvar(node, receiver_symbol):
			# 期待値: receiver.on
			cvar_key = CVars.key_from(receiver_symbol)
			operator = CVars.to_operator(cvar_key).name
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': operator, 'prop': node.prop.domain_name, 'is_property': True})
		elif self.is_relay_cvar_link(node, org_receiver_symbol, receiver_symbol):
			# 期待値: receiver.on().prop
			cvar_receiver = PatternParser.sub_cvar_relay(receiver)
			# XXX contextはactualize前のインスタンスを使う
			cvar_key = CVars.key_from(org_receiver_symbol.context)
			operator = CVars.to_operator(cvar_key).name
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': cvar_receiver, 'operator': operator, 'prop': prop, 'is_property': is_property})
		elif self.is_relay_cvar_exchanger(node, receiver_symbol):
			# 期待値: receiver.raw()
			cvar_receiver = PatternParser.sub_cvar_to(receiver)
			cvar_key = CVars.key_from(receiver_symbol)
			operator = CVars.to_operator(cvar_key).name
			move = CVars.to_move(cvar_key, node.prop.domain_name)
			return self.view.render(f'{node.classification}/cvar_to', vars={'receiver': cvar_receiver, 'move': move.name})
		elif self.is_relay_type(node, org_receiver_symbol):
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.ClassDef) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Static.name, 'prop': prop, 'is_property': is_property})
		else:
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Raw.name, 'prop': prop, 'is_property': is_property})

	def is_relay_literalizer(self, node: defs.Relay, receiver_symbol: IReflection) -> bool:
		prop = node.prop.tokens
		if prop in ['__module__', '__name__', '__qualname__']:
			return True
		elif not node.receiver.is_a(defs.ThisRef) and prop in ['name', 'value'] and isinstance(receiver_symbol.types, defs.Enum):
			return True
		else:
			return False

	def is_relay_this(self, node: defs.Relay) -> bool:
		return node.receiver.is_a(defs.ThisRef)

	def is_relay_cvar(self, node: defs.Relay, receiver_symbol: IReflection) -> bool:
		if node.prop.domain_name != CVars.relay_key:
			return False

		cvar_key = CVars.key_from(receiver_symbol)
		return not CVars.is_entity(cvar_key)

	def is_relay_cvar_link(self, node: defs.Relay, org_receiver_symbol: IReflection, receiver_symbol: IReflection) -> bool:
		if not (isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.relay_key):
			return False

		# XXX contextはactualize前のインスタンスを使う
		cvar_key = CVars.key_from(org_receiver_symbol.context)
		return not CVars.is_entity(cvar_key)

	def is_relay_cvar_exchanger(self, node: defs.Relay, receiver_symbol: IReflection) -> bool:
		if node.prop.domain_name not in CVars.exchanger_keys:
			return False

		cvar_key = CVars.key_from(receiver_symbol)
		return not CVars.is_entity(cvar_key)

	def is_relay_type(self, node: defs.Relay, org_receiver_symbol: IReflection) -> bool:
		return org_receiver_symbol.impl(refs.Object).type_is(type) or isinstance(node.receiver, defs.Super)

	def on_var(self, node: defs.Var) -> str:
		org_symbol = self.reflections.type_of(node).impl(refs.Object)
		actual_symbol = Defer.new(lambda: org_symbol.actualize('type'))
		# クラスの直参照、または引数やローカル変数がクラス参照の場合
		if org_symbol.type_is(type):
			return self.view.render(node.classification, vars={'symbol': self.to_domain_name_by_class(actual_symbol.types)})
		# 上記以外のクラス系参照の場合
		elif isinstance(actual_symbol.decl, defs.ClassDef):
			return self.view.render(node.classification, vars={'symbol': self.to_domain_name_by_class(actual_symbol.types)})
		else:
			return self.view.render(node.classification, vars={'symbol': node.tokens})

	def on_class_ref(self, node: defs.ClassRef) -> str:
		symbol = self.reflections.type_of(node).impl(refs.Object).actualize('self', 'type')
		return self.to_domain_name(symbol)

	def on_this_ref(self, node: defs.ThisRef) -> str:
		return 'this'

	def on_indexer(self, node: defs.Indexer, receiver: str, keys: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block, defs.Entrypoint)
		spec, context = self.analyze_indexer_spec(node)
		vars = {'receiver': receiver, 'keys': keys, 'is_statement': is_statement}
		if spec == 'class':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'var_type': var_type})
		elif spec == 'cvar':
			return self.view.render(f'{node.classification}/{spec}', vars=vars)
		elif spec == 'slice_array':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'var_type': var_type})
		elif spec == 'slice_string':
			return self.view.render(f'{node.classification}/{spec}', vars=vars)
		elif spec == 'tuple':
			return self.view.render(f'{node.classification}/{spec}', vars={**vars, 'receiver': receiver, 'key': keys[0]})
		else:
			return self.view.render(f'{node.classification}/default', vars={**vars, 'receiver': receiver, 'key': keys[0]})

	def analyze_indexer_spec(self, node: defs.Indexer) -> tuple[str, IReflection | None]:
		receiver_symbol = Defer.new(lambda: self.reflections.type_of(node.receiver).impl(refs.Object).actualize())
		symbol = Defer.new(lambda: self.reflections.type_of(node).impl(refs.Object))
		if node.sliced:
			spec = 'slice_string' if receiver_symbol.type_is(str) else 'slice_array'
			return spec, receiver_symbol
		elif symbol.type_is(type):
			return 'class', symbol.actualize()
		elif receiver_symbol.type_is(tuple):
			return 'tuple', None
		elif not CVars.is_entity(CVars.key_from(receiver_symbol)):
			return 'cvar', None
		else:
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
			```
			### PluckMethodのシグネチャー
			* `Callable[[T, *T_Args], None]`
			```
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
		"""Note: XXX C++でUnion型の表現は不可能。期待値を仮定するのであればプライマリー型以外に無いので先頭要素のみ返却"""
		return or_types[0]

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block, defs.Entrypoint)
		spec, context = self.analyze_func_call_spec(node)
		func_call_vars = {'calls': calls, 'arguments': arguments, 'is_statement': is_statement}
		if spec == 'c_include':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_macro':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_pragma':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == 'c_func_invoke':
			receiver_raw = Defer.new(lambda: self.reflections.type_of(node.arguments[0]).impl(refs.Object).actualize())
			operator = '->' if node.arguments[0].value.is_a(defs.ThisRef) or CVars.is_addr(CVars.key_from(receiver_raw)) else '.'
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'operator': operator})
		elif spec == 'c_func_ref':
			return self.view.render(f'{node.classification}/{spec}', vars=func_call_vars)
		elif spec == PythonClassOperations.copy_constructor:
			# 期待値: 'receiver.__py_copy__'
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == 'c_type_expr':
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'var_type': var_type})
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
		elif spec.startswith('str_'):
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == 'list_copy':
			# 期待値: 'receiver.copy'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver})
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
		elif spec == 'dict_copy':
			# 期待値: 'receiver.copy'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == 'dict_get':
			# 期待値: 'receiver.get'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == 'dict_keys':
			# 期待値: 'receiver.keys'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'dict_items':
			# 期待値: 'receiver.items'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == 'dict_pop':
			# 期待値: 'receiver.pop'
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
		elif spec == 'cvar_hex':
			# 期待値: receiver.hex()
			receiver, _ = PatternParser.break_relay(calls)
			cvar_key = CVars.key_from(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'receiver': receiver, 'is_addr': CVars.is_addr(cvar_key)})
		elif spec == 'cvar_to':
			# 期待値: CP(a)
			cvar_key = CVars.key_from(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec}', vars={**func_call_vars, 'cvar_type': cvar_key})
		elif spec == 'decl_static':
			# 期待値: Embed::static({'f': func})
			return arguments[0]
		else:
			return self.view.render(f'{node.classification}/default', vars=func_call_vars)

	def analyze_func_call_spec(self, node: defs.FuncCall) -> tuple[str, IReflection | None]:
		"""Note: XXX callsは別名になる可能性があるため、ノードから取得したcallsを使用する"""
		calls_raw = Defer.new(lambda: self.reflections.type_of(node.calls).impl(refs.Object).actualize())
		if isinstance(node.calls, defs.Var):
			calls = node.calls.tokens
			if calls == c_pragma.__name__:
				return 'c_pragma', None
			elif calls == c_include.__name__:
				return 'c_include', None
			elif calls == c_macro.__name__:
				return 'c_macro', None
			elif calls == c_func_invoke.__name__:
				return 'c_func_invoke', None
			elif calls == c_func_ref.__name__:
				return 'c_func_ref', None
			if calls == isinstance.__name__:
				return 'c_type_expr', self.reflections.type_of(node.arguments[0])
			elif calls == len.__name__:
				return 'len', self.reflections.type_of(node.arguments[0])
			elif calls == print.__name__:
				return 'print', None
			elif calls == 'char':
				return 'cast_char', None
			elif calls == 'list':
				return 'cast_list', None
			elif calls in FuncCallMaps.convertion_scalars:
				to_type = FuncCallMaps.convertion_scalars[calls]
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
			elif not CVars.is_entity(CVars.key_from(calls_raw)):
				# XXX AltClassを考慮するとRelay側も対応が必要で片手落ち
				return f'cvar_to', calls_raw
		elif isinstance(node.calls, defs.Relay):
			prop = node.calls.prop.tokens
			if prop in FuncCallMaps.list_and_dict_methods:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object)
				if prop in FuncCallMaps.list_methods and receiver_raw.type_is(list):
					return f'list_{prop}', receiver_raw.attrs[0]
				elif receiver_raw.type_is(dict) and node.parent.is_a(defs.ForIn):
					# XXX for/comprehensionにより、レシーバー自体がイテレーターとして評価されるため、通常の関数コールとして処理
					return 'otherwise', None
				elif receiver_raw.type_is(dict):
					key_attr, value_attr = receiver_raw.attrs
					prop_to_context = {'pop': value_attr, 'keys': key_attr, 'values': value_attr, 'items': receiver_raw, 'get': value_attr, 'copy': receiver_raw}
					return f'dict_{prop}', prop_to_context[prop]
			elif prop == PythonClassOperations.copy_constructor:
				return prop, None
			elif prop in FuncCallMaps.str_methods:
				if node.calls.receiver.is_a(defs.String):
					return f'str_{prop}', None
				elif self.reflections.type_of(node.calls.receiver).impl(refs.Object).type_is(str):
					return f'str_{prop}', None
			elif prop == CVars.copy_key:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = CVars.key_from(receiver_raw)
				if CVars.is_raw_ref(cvar_key):
					return 'cvar_copy', None
			elif prop == CVars.empty_key and isinstance(node.calls.receiver, defs.Indexer):
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = CVars.key_from(receiver_raw)
				if CVars.is_addr_sp(cvar_key):
					# 期待値: CSP[A] | None
					entity_raw = self.reflections.type_of(node).attrs[0].attrs[0]
					return 'cvar_sp_empty', entity_raw
			elif prop == CVars.allocator_key and isinstance(node.calls.receiver, defs.Var):
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = CVars.key_from(receiver_raw)
				if CVars.is_addr_p(cvar_key):
					return 'cvar_new_p', None
				elif CVars.is_addr_sp(cvar_key):
					new_type_raw = self.reflections.type_of(node.arguments[0])
					spec = 'cvar_new_sp_list' if new_type_raw.impl(refs.Object).type_is(list) else 'cvar_new_sp'
					return spec, new_type_raw
			elif prop == CVars.hex_key:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = CVars.key_from(receiver_raw)
				if not CVars.is_entity(cvar_key):
					return 'cvar_hex', receiver_raw
			elif prop == Embed.static.__name__ and node.calls.tokens == Embed.static.__qualname__:
				return 'decl_static', None

		if isinstance(node.calls, (defs.Relay, defs.Var)):
			if len(node.arguments) > 0 and node.arguments[0].value.is_a(defs.Reference):
				primary_arg_raw = self.reflections.type_of(node.arguments[0])
				if primary_arg_raw.impl(refs.Object).type_is(type):
					return 'generic_call', None

			if calls_raw.types.is_a(defs.Enum):
				return 'cast_enum', calls_raw

		return 'otherwise', None

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		parent_symbol = self.reflections.type_of(node)
		return self.to_accessible_name(parent_symbol)

	def on_for_in(self, node: defs.ForIn, iterates: str) -> str:
		return iterates

	def on_comp_for(self, node: defs.CompFor, symbols: list[str], for_in: str) -> str:
		# XXX is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		for_in_symbol = Defer.new(lambda: self.reflections.type_of(node.for_in).impl(refs.Object).actualize())
		is_const = CVars.is_const(CVars.key_from(for_in_symbol)) if len(symbols) == 1 else False
		is_addr_p = CVars.is_addr(CVars.key_from(for_in_symbol)) if len(symbols) == 1 else False

		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens in [range.__name__, enumerate.__name__]:
			spec = node.iterates.calls.tokens
			return self.view.render(f'comp/{node.classification}_{spec}', vars={'symbols': symbols, 'iterates': for_in, 'is_const': is_const, 'is_addr_p': is_addr_p})
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) \
			and node.iterates.calls.prop.tokens in [dict.items.__name__, dict.keys.__name__, dict.values.__name__] \
			and self.reflections.type_of(node.iterates.calls.receiver).impl(refs.Object).actualize().type_is(dict):
			# 期待値: 'iterates.items()'
			receiver, operator, method_name = PatternParser.break_dict_iterator(for_in)
			# XXX 参照の変換方法が場当たり的で一貫性が無い。包括的な対応を検討
			iterates = f'*({receiver})' if operator == '->' else receiver
			dict_symbols = {dict.items.__name__: symbols, dict.keys.__name__: [symbols[0], '_'], dict.values.__name__: ['_', symbols[0]]}
			return self.view.render(f'comp/{node.classification}', vars={'symbols': dict_symbols[method_name], 'iterates': iterates, 'is_const': is_const, 'is_addr_p': False})
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
		projection_key, projection_value = BlockParser.break_separator(projection[1:-1], ',')
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
		primary_raw = left_raw
		for index, right_raw in enumerate(right_raws):
			operator = operators[index]
			secondary = rights[index]
			if operator in ['in', 'not.in']:
				primary = self.view.render('binary_operator/in', vars={'left': primary, 'operator': operator, 'right': secondary, 'right_is_dict': right_raw.impl(refs.Object).type_is(dict)})
			else:
				primary = self.view.render('binary_operator/default', vars={'left': primary, 'operator': operator, 'right': secondary, 'left_var_type': self.to_domain_name(primary_raw), 'right_var_type': self.to_domain_name(right_raw)})

			primary_raw = right_raw

		return primary

	def on_ternary_operator(self, node: defs.TernaryOperator, primary: str, condition: str, secondary: str) -> str:
		return self.view.render(node.classification, vars={'primary': primary, 'condition': condition, 'secondary': secondary})

	# Literal

	def on_integer(self, node: defs.Integer) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'value': node.tokens})

	def on_float(self, node: defs.Float) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'value': node.tokens})

	def on_string(self, node: defs.String) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'value': node.tokens})

	def on_doc_string(self, node: defs.DocString) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'data': node.data})

	def on_truthy(self, node: defs.Truthy) -> str:
		return self.view.render(f'literal/{node.classification}')

	def on_falsy(self, node: defs.Falsy) -> str:
		return self.view.render(f'literal/{node.classification}')

	def on_pair(self, node: defs.Pair, first: str, second: str) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'first': first, 'second': second})

	def on_list(self, node: defs.List, values: list[str]) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'values': values})

	# XXX あまりにも非効率なため非対応
	# def proc_list_for_spread(self, node: defs.List, values: list[str], spread_indexs: list[int]) -> str:
	# 	before = 0
	# 	steps: list[tuple[int, int]] = []
	# 	for count, index in enumerate(spread_indexs):
	# 		if before < index:
	# 			steps.append((before, index))

	# 		steps.append((index, index + 1))

	# 		if count == len(spread_indexs) - 1 and index < len(values) - 1:
	# 			steps.append((index, len(values)))

	# 		before = index + 1

	# 	list_literals = [self.view.render(f'literal/{node.classification}', vars={'values': values[begin:end]}) for begin, end in steps]
	# 	return self.view.render(f'literal/{node.classification}_spread', vars={'list_literals': list_literals})

	def on_dict(self, node: defs.Dict, items: list[str]) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'items': items})

	def on_tuple(self, node: defs.Tuple, values: list[str]) -> str:
		return self.view.render(f'literal/{node.classification}', vars={'values': values})

	def on_null(self, node: defs.Null) -> str:
		return self.view.render(f'literal/{node.classification}')

	# Expression

	def on_group(self, node: defs.Group, expression: str) -> str:
		return self.view.render(node.classification, vars={'expression': expression})

	def on_spread(self, node: defs.Spread, expression: str) -> str:
		raise NotSupportedError(f'Denied spread expression. node: {node}')

	def on_lambda(self, node: defs.Lambda, expression: str) -> str:
		expression_raw = self.reflections.type_of(node.expression)
		var_type = self.to_accessible_name(expression_raw)
		return self.view.render(node.classification, vars={'expression': expression, 'var_type': var_type})

	# Terminal

	def on_terminal(self, node: Node) -> str:
		return node.tokens

	# Fallback

	def on_fallback(self, node: Node) -> str:
		return node.tokens


class ClassOperationMaps:
	"""特殊メソッドのマッピングデータ"""

	operators: ClassVar[dict[str, str]] = {
		# comparison
		'__eq__': 'operator==',
		'__ne__': 'operator!=',
		'__lt__': 'operator<',
		'__gt__': 'operator>',
		'__le__': 'operator<=',
		'__ge__': 'operator>=',
		# arithmetic
		'__add__': 'operator+',
		'__sub__': 'operator-',
		'__mul__': 'operator*',
		'__mod__': 'operator%',
		'__truediv__': 'operator/',
		# bitwise
		'__and__': 'operator&',
		'__or__': 'operator|',
		# indexer
		'__getitem__': 'operator[]',
		# '__setitem__': 'operator[]', XXX C++ではset用のオペレーターは存在せず、getから参照を返すことで実現する
	}

	ctors: ClassVar[dict[str, str]] = {
		PythonClassOperations.copy_constructor: 'copy_constructor',
		PythonClassOperations.destructor: 'destructor',
	}


class FuncCallMaps:
	"""FuncCall用のマッピングデータ"""

	convertion_scalars: ClassVar[dict[str, type[bool | int | float | str]]] = {
		bool.__name__: bool,
		int.__name__: int,
		float.__name__: float,
		str.__name__: str,
	}
	list_methods: ClassVar[list[str]] = [
		list.pop.__name__,
		list.insert.__name__,
		list.extend.__name__,
		list.copy.__name__,
	]
	list_and_dict_methods: ClassVar[list[str]] = [
		list.pop.__name__,
		list.insert.__name__,
		list.extend.__name__,
		dict.items.__name__,
		dict.keys.__name__,
		dict.values.__name__,
		dict.get.__name__,
		dict.copy.__name__,
	]
	str_methods: ClassVar[list[str]] = [
		str.split.__name__,
		str.join.__name__,
		str.replace.__name__,
		str.lstrip.__name__,
		str.rstrip.__name__,
		str.strip.__name__,
		str.find.__name__,
		str.rfind.__name__,
		str.count.__name__,
		str.startswith.__name__,
		str.endswith.__name__,
		str.format.__name__,
		str.encode.__name__,
	]


class PatternParser:
	"""正規表現によるパターン解析ユーティリティー

	Note:
		これらは正規表現を用いないで済む方法へ修正を検討
	"""

	RelayPattern = re.compile(r'(.+)(->|::|\.)\w+$')
	DictIteratorPattern = re.compile(r'(.+)(->|\.)(\w+)\(\)$')
	DeclClassVarNamePattern = re.compile(r'\s+([\w\d_]+)\s+=')
	MoveDeclRightPattern = re.compile(r'=\s*([^;]+);$')
	InitDeclRightPattern = re.compile(r'({[^;]*});$')
	CVarRelaySubPattern = re.compile(rf'(->|::|\.){CVars.relay_key}\(\)$')
	CVarToSubPattern = re.compile(rf'(->|::|\.)({"|".join(CVars.exchanger_keys)})\(\)$')

	@classmethod
	def break_relay(cls, relay: str) -> tuple[str, str]:
		"""リレーからレシーバーとオペレーターに分解

		Args:
			relay: 文字列
		Returns:
			(レシーバー, オペレーター)
		Note:
			```
			### 期待値
			'path.to->prop' -> ('path.to', '->')
			```
		"""
		return cast(re.Match, cls.RelayPattern.fullmatch(relay)).group(1, 2)

	@classmethod
	def pluck_func_call_arguments(cls, func_call: str) -> str:
		"""関数コールから引数リストの部分を抜き出す

		Args:
			func_call: 文字列
		Returns:
			引数リスト
		Note:
			```
			### 期待値
			'path.to.calls(arguments...)' -> 'arguments...'
			```
		"""
		return BlockParser.break_last_block(func_call, '()')[1]

	@classmethod
	def break_dict_iterator(cls, func_call: str) -> tuple[str, str, str]:
		"""連想配列のイテレーターコール(items|keys|values)から各要素に分解

		Args:
			func_call: 文字列
		Returns:
			(レシーバー, オペレーター, メソッド)
		Note:
			```
			### 期待値
			'path.to->items()' -> ('path.to', '->', 'items')
			```
		"""
		return cast(re.Match, cls.DictIteratorPattern.fullmatch(func_call)).group(1, 2, 3)

	@classmethod
	def pluck_super_arguments(cls, func_call: str) -> str:
		"""関数コール(super)から引数リストの部分を抜き出す

		Args:
			func_call: 文字列
		Returns:
			引数リスト
		Note:
			```
			### 期待値
			'Class::__init__(arguments...);' -> 'arguments...'
			```
		"""
		return BlockParser.break_last_block(func_call, '()')[1]

	@classmethod
	def pluck_class_var_name(cls, decl_class_var: str) -> str:
		"""代入式から右辺の部分を抜き出す

		Args:
			assign: 文字列
		Returns:
			右辺
		Note:
			```
			### 期待値
			'A var_name = right;' -> 'var_name'
			```
		"""
		matches = cls.DeclClassVarNamePattern.search(decl_class_var)
		return matches[1] if matches else ''

	@classmethod
	def pluck_decl_right(cls, assign: str) -> str:
		"""変数宣言時の代入式から右辺の部分を抜き出す

		Args:
			assign: 文字列
		Returns:
			右辺
		Note:
			```
			### 期待値
			'path.to = right;' -> 'right'
			'path.to{right};' -> '{right}'
			```
		"""
		matches = cls.MoveDeclRightPattern.search(assign)
		if matches:
			return matches[1]

		matches = cls.InitDeclRightPattern.search(assign)
		return matches[1] if matches else ''

	@classmethod
	def break_indexer(cls, indexer: str) -> tuple[str, str]:
		"""インデクサーからレシーバーとキーに分解

		Args:
			assign: 文字列
		Returns:
			(レシーバー, キー)
		Note:
			```
			### 期待値
			'path.to[key]' -> ('path.to', 'key')
			```
		"""
		return BlockParser.break_last_block(indexer, '[]')

	@classmethod
	def pluck_cvar_new_argument(cls, argument: str) -> str:
		"""C++型変数のメモリー生成関数コールから引数の部分を抜き出す

		Args:
			argument: 文字列
		Returns:
			引数
		Note:
			```
			### 期待値
			'Class(arguments...)' -> 'arguments...'
			```
		"""
		return BlockParser.break_last_block(argument, '()')[1]

	@classmethod
	def sub_cvar_relay(cls, receiver: str) -> str:
		"""C++型変数のリレープロクシーを削除する

		Args:
			receiver: 文字列
		Returns:
			引数
		Note:
			```
			### 期待値
			'path.on()->to' -> 'path.to'
			```
		"""
		return cls.CVarRelaySubPattern.sub('', receiver)

	@classmethod
	def sub_cvar_to(cls, receiver: str) -> str:
		"""C++型変数の型変換プロクシーを削除する

		Args:
			receiver: 文字列
		Returns:
			引数
		Note:
			```
			### 期待値
			'path.to.raw()' -> 'path.to'
			```
		"""
		return cls.CVarToSubPattern.sub('', receiver)
