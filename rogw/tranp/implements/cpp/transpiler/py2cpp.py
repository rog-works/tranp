import re
from collections.abc import Callable
from enum import Enum
from typing import Any, ClassVar, Protocol, Self, TypeVarTuple, cast, override

import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.compatible.cpp.classes import byte, char, double, int64, uint32, uint64
from rogw.tranp.compatible.cpp.cvar import CP, CWP
from rogw.tranp.compatible.cpp.function import c_func_invoke, c_func_ref
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma
from rogw.tranp.compatible.python.embed import Embed
from rogw.tranp.compatible.python.types import Union
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory, TranspilerMeta
from rogw.tranp.data.version import Versions
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn, import_dsn
from rogw.tranp.errors import Errors
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.defer import Defer
from rogw.tranp.lang.eventemitter import Callback, Observable
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.semantics.procedure import Procedure
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.helper.naming import ClassDomainNaming, ClassShorthandNaming
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.node.definition.accessible import PythonClassOperations
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.transpiler.types import Evaluator, ITranspiler, TranspilerOptions
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.render import Renderer, RendererEmitter


class Py2Cpp(ITranspiler):
	"""Python -> C++のトランスパイラー"""

	@injectable
	def __init__(self, reflections: Reflections, render: Renderer, i18n: I18n, evaluator: Evaluator, emitter: RendererEmitter, module_meta_factory: ModuleMetaFactory, options: TranspilerOptions) -> None:
		"""インスタンスを生成

		Args:
			reflections: シンボルリゾルバー @inject
			render: ソースレンダー @inject
			i18n: 国際化対応モジュール @inject
			evaluator: リテラル演算モジュール @inject
			emitter: レンダー用イベントエミッター @inject
			module_meta_factory: モジュールのメタ情報ファクトリー @inject
			options: 実行オプション @inject
		"""
		self.reflections = reflections
		self.view = render
		self.i18n = i18n
		self.evaluator = evaluator
		self.module_meta_factory = module_meta_factory
		self.include_dirs = self.__make_include_dirs(options)
		# XXX config.ymlから設定を読み込む想定だが、不完全なため現状は非対応
		self.cvars = CVars()
		self.__procedure = self.__make_procedure(options)
		# XXX トランスパイラーがステートフルになってしまう上、処理中のモジュールとの結合が曖昧
		self.__stack_on_depends: list[list[str]] = []
		emitter.on('depends', self.__on_view_depends)

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

	def __on_view_depends(self, path: str) -> None:
		"""ビュー由来の依存追加イベントを受信

		Args:
			path: 依存パス
		Note:
			```
			### 依存パスの期待値
			* "path/to/name.h"
			* <functional>
			```
		Examples:
			```jinja2
			{{- emit_depends('"path/to/name.h"') -}}
			```
		Raises:
			Errors.InvalidSchema: 依存パスの書式が不正
		"""
		if not re.fullmatch(r'"[\w\d/]+.h"|<[\w\d/]+>', path):
			raise Errors.InvalidSchema(path)

		if path not in self.__stack_on_depends[-1]:
			self.__stack_on_depends[-1].append(path)

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
	@override
	def meta(self) -> TranspilerMeta:
		"""Returns: トランスパイラーのメタ情報"""
		return {'version': Versions.py2cpp, 'module': to_fullyname(Py2Cpp)}

	@override
	def transpile(self, node: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			node: 起点のノード
		Returns:
			トランスパイル後のソースコード
		"""
		# XXX トランスパイル毎に依存スタックを生成
		self.__stack_on_depends.append([])
		result = self.__procedure.exec(node)
		self.__stack_on_depends.pop()
		return result

	def explicit_class_attrs(self, raw: IReflection) -> list[IReflection]:
		"""トランスパイル上で明示が必要なクラスのサブタイプを抽出

		Args:
			raw: シンボル(クラス)
		Returns:
			属性リスト
		Note:
			クラス自身が持つテンプレート型の属性を明示するべきシグネチャーとして抽出
		"""
		# 属性なし
		actual_attrs = raw.attrs
		if len(actual_attrs) == 0:
			return actual_attrs

		# tuple/Union/Callable XXX 可変長のため許容 ※TypeVarTupleに対応すれば特殊化せずに済むが、一旦簡易的な実装とする
		raw_obj = raw.impl(refs.Object)
		if raw_obj.type_is(tuple) or raw_obj.type_is(Union) or raw_obj.type_is(Callable):
			return actual_attrs

		decl_attrs: list[IReflection] = []
		for sub_type in raw.types.as_a(defs.Class).depended_types:
			attr = self.reflections.type_of(sub_type)
			if sub_type.is_a(defs.TemplateClass):
				# XXX タイプ参照と形式を合わせるためtypeをアンパック
				# @see ConvertionTrait._actualize_type
				# @see SymbolExtends.attr_for_class
				decl_attrs.append(attr.attrs[0])
			else:
				decl_attrs.append(attr)

		# TypeVarTuple XXX 可変長のため許容 ※主な対象: Delegate
		has_type_var_tuple = len([True for decl_attr in decl_attrs if isinstance(decl_attr.types, defs.TemplateClass) and decl_attr.types.definition_type.type_name.tokens == TypeVarTuple.__name__]) > 0
		if has_type_var_tuple:
			return actual_attrs

		if len(actual_attrs) != len(decl_attrs):
			raise Errors.Never(raw)

		return [attr for index, attr in enumerate(actual_attrs) if decl_attrs[index].types.is_a(defs.TemplateClass)]

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
		var_type = ClassDomainNaming.accessible_name(actual_raw.types, alias_handler=self.i18n.t, alias_transpiler=self.transpile)
		if actual_raw.types.is_a(defs.Method):
			var_type = self.to_accessible_name_for_method(actual_raw, var_type, [self.to_accessible_name(attr) for attr in actual_raw.attrs])
		elif actual_raw.types.is_a(defs.ClassMethod):
			var_type = self.to_accessible_name_for_class_method(actual_raw, var_type, [self.to_accessible_name(attr) for attr in actual_raw.attrs])
		elif actual_raw.types.is_a(defs.Function):
			var_type = self.to_accessible_name_for_function(actual_raw, var_type, [self.to_accessible_name(attr) for attr in actual_raw.attrs])
		elif actual_raw.type_is(Callable):
			var_type = self.to_accessible_name_for_callable(actual_raw, var_type, [self.to_accessible_name(attr) for attr in actual_raw.attrs])
		elif actual_raw.types.is_a(defs.Class):
			var_type = self.to_accessible_name_for_class(actual_raw, var_type, [self.to_accessible_name(attr) for attr in self.explicit_class_attrs(actual_raw)])
		elif actual_raw.types.is_a(defs.AltClass):
			var_type = self.to_accessible_name_for_alt_class(actual_raw, var_type)

		var_type = self.view.render('type_py2cpp', vars={'var_type': var_type})
		return DSN.join(*DSN.elements(var_type), delimiter='::')

	def to_accessible_name_for_method(self, raw: IReflection, var_type: str, attrs: list[str]) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(Method)"""
		# FIXME アノテーションを考慮しておらず場当たり的な対応
		param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attrs[1:-1]]
		return f'{attrs[-1]}({DSN.join(*DSN.elements(var_type)[:-1])}::*)({", ".join(param_types)})'

	def to_accessible_name_for_class_method(self, raw: IReflection, var_type: str, attrs: list[str]) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(ClassMethod)"""
		param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attrs[1:-1]]
		return f'{attrs[-1]}(*)({", ".join(param_types)})'

	def to_accessible_name_for_function(self, raw: IReflection, var_type: str, attrs: list[str]) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(Function)"""
		param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attrs[:-1]]
		return f'{attrs[-1]}(*)({", ".join(param_types)})'

	def to_accessible_name_for_callable(self, raw: IReflection, var_type: str, attrs: list[str]) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(Callable)"""
		param_types = [self.view.render('param_type_py2cpp', vars={'var_type': attr_type}) for attr_type in attrs[:-1]]
		return f'{var_type}<{attrs[-1]}({", ".join(param_types)})>'

	def to_accessible_name_for_class(self, raw: IReflection, var_type: str, attrs: list[str]) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(Class)"""
		if len(attrs) > 0:
			return f'{var_type}<{", ".join(attrs)}>'
		else:
			return var_type

	def to_accessible_name_for_alt_class(self, raw: IReflection, var_type: str) -> str:
		"""型推論によって補完する際の名前空間上の参照名を取得(AltClass)"""
		if not self.cvars.is_entity(self.cvars.var_name_from(raw.attrs[0])):
			# XXX C++型変数のAltClassの特殊化であり、一般解に程遠いため修正を検討
			return f'{var_type}<{", ".join([self.to_accessible_name(attr) for attr in raw.attrs[0].attrs])}>'
		else:
			return var_type

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
		return ClassShorthandNaming.domain_name(actual_type_raw, alias_handler=self.i18n.t, alias_transpiler=self.transpile)

	def to_domain_name_by_class(self, types: defs.ClassDef) -> str:
		"""明示された型からドメイン名を取得

		Args:
			types: クラス宣言ノード
		Returns:
			型の参照名
		"""
		return ClassDomainNaming.domain_name(types, alias_handler=self.i18n.t, alias_transpiler=self.transpile)

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
		var_type_key = self.cvars.var_name_from(var_type_raw.impl(refs.Object).actualize())
		return self.cvars.is_addr(var_type_key) and null_type_raw.impl(refs.Object).type_is(None)

	def to_accessor(self, accessor: str) -> str:
		"""アクセス修飾子を翻訳

		Args:
			accessor: アクセス修飾子
		Returns:
			翻訳後のアクセス修飾子
		"""
		return self.i18n.t(ModuleDSN.full_joined(self.i18n.t(alias_dsn('lang')), 'accessor', accessor))

	def make_lambda_binds(self, node: defs.Closure | defs.Lambda) -> list[str]:
		"""ラムダ用のキャプチャー変数名リストを生成

		Args:
			node: ノード(Closure/Lambda)
		Returns:
			キャプチャー変数名リスト
		"""
		vars: list[defs.Var] = []
		for var in node.ref_vars():
			var_raw = self.reflections.type_of(var).impl(refs.Object)
			if var_raw.type_is(type) or var_raw.types.is_a(defs.Function):
				continue

			vars.append(var)

		return list({var.domain_name if not isinstance(var, defs.ThisRef) else self.view.render('this_ref'): True for var in vars}.keys())

	def make_depends(self, statements: list[str]) -> list[str]:
		"""依存パスリストを生成

		Args:
			statements: ステートメントリスト
		Returns:
			依存パスリスト
		"""
		depends = self.__stack_on_depends[-1].copy()
		in_include = False
		for statement in statements:
			if not statement.startswith('#include'):
				if in_include:
					break
				else:
					continue

			in_include = True
			include_path = statement.split(' ')[1]
			if include_path in depends:
				depends.remove(include_path)

		return depends

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		meta_header = MetaHeader(self.module_meta_factory(node.module_path), self.meta)
		return self.view.render(node.classification, vars={'statements': statements, 'meta_header': meta_header.to_header_str(), 'module_path': node.module_path, 'depends': self.make_depends(statements)})

	# Statement - compound

	def on_else_if(self, node: defs.ElseIf, condition: str, statements: list[str]) -> str:
		return self.view.render(f'if/{node.classification}', vars={'condition': condition, 'statements': statements})

	def on_else(self, node: defs.Else, statements: list[str]) -> str:
		return self.view.render(f'if/{node.classification}', vars={'statements': statements})

	def on_if(self, node: defs.If, condition: str, statements: list[str], else_ifs: list[str], else_clause: str) -> str:
		return self.view.render(f'if/{node.classification}', vars={'condition': condition, 'statements': statements, 'else_ifs': else_ifs, 'else_clause': else_clause})

	def on_while(self, node: defs.While, condition: str, statements: list[str]) -> str:
		return self.view.render(f'flow/{node.classification}', vars={'condition': condition, 'statements': statements})

	def on_for(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == range.__name__:
			return self.proc_for_range(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens == enumerate.__name__:
			return self.proc_for_enumerate(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) \
			and node.iterates.calls.prop.tokens in FuncCallSpec.dict_iter_methods \
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
		is_const = self.cvars.is_const(self.cvars.var_name_from(for_in_symbol)) if len(symbols) == 1 else False
		# 期待値: 'iterates.items()'
		receiver, operator, _ = PatternParser.break_dict_iterator(for_in)
		method_name = node.iterates.as_a(defs.FuncCall).calls.as_a(defs.Relay).prop.tokens
		# XXX 参照の変換方法が場当たり的で一貫性が無い。包括的な対応を検討
		iterates = f'*({receiver})' if operator == '->' else receiver
		dict_symbols = {dict.items.__name__: symbols, dict.keys.__name__: [symbols[0], '_'], dict.values.__name__: ['_', symbols[0]]}
		return self.view.render(f'{node.classification}/dict', vars={'symbols': dict_symbols[method_name], 'iterates': iterates, 'statements': statements, 'is_const': is_const, 'is_addr_p': False})

	def proc_for_each(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		# XXX is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		for_in_symbol = Defer.new(lambda: self.reflections.type_of(node.for_in).impl(refs.Object).actualize())
		is_const = self.cvars.is_const(self.cvars.var_name_from(for_in_symbol)) if len(symbols) == 1 else False
		is_addr_p = self.cvars.is_addr_p(self.cvars.var_name_from(for_in_symbol)) if len(symbols) == 1 else False
		return self.view.render(f'{node.classification}/default', vars={'symbols': symbols, 'iterates': for_in, 'statements': statements, 'is_const': is_const, 'is_addr_p': is_addr_p})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(f'flow/{node.classification}', vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(f'flow/{node.classification}', vars={'statements': statements, 'catches': catches})

	def on_with_entry(self, node: defs.WithEntry, enter: str, symbol: str) -> str:
		return self.view.render(f'flow/{node.classification}', vars={'enter': enter, 'symbol': symbol})

	def on_with(self, node: defs.With, statements: list[str], entries: list[str]) -> str:
		return self.view.render(f'flow/{node.classification}', vars={'statements': statements, 'entries': entries})

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], template_params: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		template_types = {template_name: True for template_name in [*template_params, *self.fetch_function_template_names(node)]}.keys()
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		return self.view.render(f'function/{node.classification}', vars=function_vars)

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], template_params: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = {template_name: True for template_name in [*template_params, *self.fetch_function_template_names(node)]}.keys()
		return_type_annotation = self.transpile(node.return_type.annotation) if not isinstance(node.return_type.annotation, defs.Empty) else ''
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'return_type_annotation': return_type_annotation}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars})

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], template_params: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
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
			# 期待値: `Class::__init__(a, b, c);`
			super_class, super_args = PatternParser.break_super_call(super_initializer_statement)
			super_initializer['parent'] = super_class
			super_initializer['arguments'] = super_args

		# メンバー変数の宣言用のデータを生成
		initializers: list[dict[str, str]] = []
		for index, this_var in enumerate(this_vars):
			# 期待値: `this->a = 1234;`
			initial_value = PatternParser.pluck_decl_right(initializer_statements[index])
			initializer = {'symbol': self.i18n.t(alias_dsn(this_var.fullyname), this_var.domain_name), 'value': initial_value}
			initializers.append(initializer)

		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = {template_name: True for template_name in [*template_params, *self.fetch_function_template_names(node)]}.keys()
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': normal_statements, 'template_types': template_types}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'allow_override': self.allow_override_from_method(node)}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, **method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], template_params: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		class_name = self.to_domain_name_by_class(node.class_types)
		template_types = {template_name: True for template_name in [*template_params, *self.fetch_function_template_names(node)]}.keys()
		return_type_annotation = self.transpile(node.return_type.annotation) if not isinstance(node.return_type.annotation, defs.Empty) else ''
		_symbol = ClassOperationMaps.operators.get(symbol, symbol)
		function_vars = {'symbol': _symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'comment': comment, 'statements': statements, 'template_types': template_types, 'is_pure': node.is_pure}
		method_vars = {'accessor': self.to_accessor(node.accessor), 'class_symbol': class_name, 'is_abstract': node.is_abstract, 'is_override': node.is_override, 'is_property': node.is_property, 'allow_override': self.allow_override_from_method(node), 'return_type_annotation': return_type_annotation}
		spec = ClassOperationMaps.ctors.get(symbol, node.classification)
		return self.view.render(f'function/{spec}', vars={**function_vars, **method_vars})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], template_params: list[str], parameters: list[str], return_type: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'statements': statements}
		return self.view.render(f'function/{node.classification}', vars={**function_vars, 'binds': self.make_lambda_binds(node)})

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], template_params: list[str], inherits: list[str], inherit_sub_types: list[str], comment: str, statements: list[str]) -> str:
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

		# XXX サブタイプからテンプレートタイプを抽出
		template_types = template_params.copy()
		for index, sub_type in enumerate(node.inherit_sub_types):
			if inherit_sub_types[index] not in template_types and self.reflections.type_of(sub_type).types.is_a(defs.TemplateClass):
				template_types.append(inherit_sub_types[index])

		accessor = self.to_accessor(node.accessor) if node.is_internal else ''

		class_vars = {'accessor': accessor, 'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'template_types': template_types, 'comment': comment, 'statements': a_statements, 'module_path': node.module_path}
		return self.view.render(f'{node.classification}/class', vars=class_vars)

	def on_enum(self, node: defs.Enum, symbol: str, decorators: list[str], template_params: list[str], inherits: list[str], inherit_sub_types: list[str], comment: str, statements: list[str]) -> str:
		accessor = self.to_accessor(node.accessor) if node.is_internal else ''
		return self.view.render(f'class/{node.classification}', vars={'accessor': accessor, 'symbol': symbol, 'decorators': decorators, 'comment': comment, 'statements': statements, 'module_path': node.module_path})

	def on_alt_class(self, node: defs.AltClass, symbol: str, actual_type: str) -> str:
		accessor = self.to_accessor(node.accessor) if node.is_internal else ''
		return self.view.render(f'class/{node.classification}', vars={'accessor': accessor, 'symbol': symbol, 'actual_type': actual_type})

	def on_template_class(self, node: defs.TemplateClass, symbol: str) -> str:
		is_declare = node.parent.is_a(defs.Block, defs.Entrypoint)
		return self.view.render(f'class/{node.classification}', vars={'symbol': symbol, 'is_declare': is_declare})

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
			raise Errors.OperationNotAllowed(node, value_raw, 'Reject assign. Must be Nullable or Non-Union')

		var_type = self.to_accessible_name(value_raw)
		assign_vars = {'receiver': receiver, 'var_type': var_type, 'value': value}
		if not declared:
			return self.view.render(f'assign/{node.classification}', vars=assign_vars)
		elif isinstance(node.value, defs.FuncCall) and node.value.calls.tokens.startswith(Embed.static.__qualname__):
			return self.view.render(f'assign/{node.classification}_declare', vars={**assign_vars, 'is_static': True})
		elif isinstance(node.value, defs.FuncCall) and value.startswith(f'{var_type}('):
			return self.view.render(f'assign/{node.classification}_declare', vars={**assign_vars, 'is_initializer': True})
		else:
			return self.view.render(f'assign/{node.classification}_declare', vars=assign_vars)

	def proc_move_assign_destruction(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		"""Note: C++で分割代入できるのはtuple/pairのみ。Pythonではいずれもtupleのため、tuple以外は非対応"""
		value_raw = self.reflections.type_of(node.value).impl(refs.Object).actualize()
		if not value_raw.type_is(tuple):
			raise Errors.OperationNotAllowed(node, 'Reject assign. Must be a tuple')

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
				raise Errors.OperationNotAllowed(node, target_node, 'Reject delete. Must be list or dict')

			target_symbol = self.reflections.type_of(target_node.receiver)
			target_types.append('list' if target_symbol.impl(refs.Object).type_is(list) else 'dict')

		_targets: list[dict[str, str]] = []
		for i in range(len(targets)):
			target = targets[i]
			receiver, key = PatternParser.break_indexer(target)
			_targets.append({'receiver': receiver, 'key': key, 'list_or_dict': target_types[i]})

		return self.view.render(f'statement/{node.classification}', vars={'targets': _targets})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		return self.view.render(f'statement/{node.classification}', vars={'return_value': return_value, 'return_self': node.return_value.is_a(defs.ThisRef)})

	def on_yield(self, node: defs.Yield, yield_value: str) -> str:
		return self.view.render(f'statement/{node.classification}', vars={'yield_value': yield_value})

	def on_assert(self, node: defs.Assert, condition: str, assert_body: str) -> str:
		return self.view.render(f'statement/{node.classification}', vars={'condition': condition, 'assert_body': assert_body})

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(f'statement/{node.classification}', vars={'throws': throws, 'via': via, 'is_new': node.throws.is_a(defs.FuncCall)})

	def on_pass(self, node: defs.Pass) -> str:
		# XXX statementsのスタック数が合わなくなるため出力
		return ''

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_comment(self, node: defs.Comment) -> str:
		return self.view.render(f'statement/{node.classification}', vars={'text': node.text})

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
			return self.view.render(f'statement/{node.classification}_i18n', vars={'import_path': text})

		import_dir = ''
		replace_dir = ''
		for in_import, in_replace in self.include_dirs.items():
			if len(import_dir) < len(in_import) and module_path.startswith(in_import.replace('/', '.')):
				import_dir = in_import
				replace_dir = in_replace

		return self.view.render(f'statement/{node.classification}', vars={'module_path': module_path, 'import_dir': import_dir, 'replace_dir': replace_dir, 'symbols': symbols})

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
		is_statement = node.parent.is_a(defs.Block, defs.Entrypoint)
		org_receiver_symbol = Defer.new(lambda: self.reflections.type_of(node.receiver).impl(refs.Object))
		receiver_symbol = Defer.new(lambda: org_receiver_symbol.actualize())
		prop_symbol = Defer.new(lambda: receiver_symbol.prop_of(node.prop))
		if self.is_relay_literalizer(node, receiver_symbol):
			org_prop = node.prop.domain_name
			if org_prop == '__name__':
				# XXX 'alt'の実体化を除外
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'is_statement': is_statement, 'literal': self.to_domain_name_by_class(org_receiver_symbol.actualize('type').types)})
			elif org_prop == '__module__':
				# XXX 'alt'の実体化を除外
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'is_statement': is_statement, 'literal': org_receiver_symbol.actualize('type').types.module_path})
			elif org_prop == 'name':
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'is_statement': is_statement, 'literal': node.receiver.as_a(defs.Relay).prop.tokens})
			elif org_prop == 'value':
				var_name = DSN.right(node.receiver.domain_name, 1)
				var_value = receiver_symbol.types.as_a(defs.Enum).var_value(var_name)
				var_symbol = self.reflections.type_of(var_value).impl(refs.Object)
				var_type = self.to_domain_name(var_symbol)
				literal = var_value.tokens if var_value.is_a(defs.Literal) else str(self.evaluator.exec(var_value))
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': var_type, 'is_statement': is_statement, 'literal': literal[1:-1] if var_symbol.type_is(str) else literal})
			else:
				return self.view.render(f'{node.classification}/literalize', vars={'prop': org_prop, 'var_type': str.__name__, 'is_statement': is_statement, 'literal': receiver})
		elif self.is_relay_this(node):
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Address.name, 'prop': prop, 'is_statement': is_statement, 'is_property': is_property})
		elif self.is_relay_cvar(node, receiver_symbol):
			# 期待値: receiver.on
			cvar_key = self.cvars.var_name_from(receiver_symbol)
			operator = self.cvars.to_operator(cvar_key).name
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': operator, 'prop': node.prop.domain_name, 'is_statement': is_statement, 'is_property': True})
		elif self.is_relay_cvar_link(node, org_receiver_symbol, receiver_symbol):
			# 期待値: receiver.on().prop
			cvar_receiver = PatternParser.sub_cvar_relay(receiver)
			# XXX contextはactualize前のインスタンスを使う
			cvar_key = self.cvars.var_name_from(org_receiver_symbol.context)
			operator = self.cvars.to_operator(cvar_key).name
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': cvar_receiver, 'operator': operator, 'prop': prop, 'is_statement': is_statement, 'is_property': is_property})
		elif self.is_relay_cvar_cast(node, receiver_symbol):
			# 期待値: receiver.raw()
			cvar_receiver = PatternParser.sub_cvar_to(receiver)
			cvar_key = self.cvars.var_name_from(receiver_symbol)
			operator = self.cvars.to_operator(cvar_key).name
			move = self.cvars.to_move(cvar_key, node.prop.domain_name)
			return self.view.render(f'{node.classification}/cvar_to', vars={'receiver': cvar_receiver, 'move': move.name, 'is_statement': is_statement})
		elif self.is_relay_type(node, org_receiver_symbol):
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.ClassDef) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Static.name, 'prop': prop, 'is_statement': is_statement, 'is_property': is_property})
		else:
			prop = self.to_domain_name_by_class(prop_symbol.types) if isinstance(prop_symbol.decl, defs.Method) else self.to_prop_name(prop_symbol)
			is_property = isinstance(prop_symbol.decl, defs.Method) and prop_symbol.decl.is_property
			return self.view.render(f'{node.classification}/default', vars={'receiver': receiver, 'operator': CVars.RelayOperators.Raw.name, 'prop': prop, 'is_statement': is_statement, 'is_property': is_property})

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
		if node.prop.domain_name != CVars.Verbs.On.value:
			return False

		cvar_key = self.cvars.var_name_from(receiver_symbol)
		return not self.cvars.is_entity(cvar_key)

	def is_relay_cvar_link(self, node: defs.Relay, org_receiver_symbol: IReflection, receiver_symbol: IReflection) -> bool:
		if not (isinstance(node.receiver, defs.Relay) and node.receiver.prop.domain_name == CVars.Verbs.On.value):
			return False

		# XXX contextはactualize前のインスタンスを使う
		cvar_key = self.cvars.var_name_from(org_receiver_symbol.context)
		return not self.cvars.is_entity(cvar_key)

	def is_relay_cvar_cast(self, node: defs.Relay, receiver_symbol: IReflection) -> bool:
		if  not CVars.Casts.in_value(node.prop.domain_name):
			return False

		cvar_key = self.cvars.var_name_from(receiver_symbol)
		return not self.cvars.is_entity(cvar_key)

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
		return self.view.render(node.classification)

	def on_indexer(self, node: defs.Indexer, receiver: str, keys: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block, defs.Entrypoint)
		spec, context = self.analyze_indexer_spec(node)
		vars = {'receiver': receiver, 'keys': keys, 'is_statement': is_statement}
		if spec == IndexerSpec.Tags.klass:
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/class', vars={**vars, 'var_type': var_type})
		elif spec == IndexerSpec.Tags.cvar:
			return self.view.render(f'{node.classification}/{spec.name}', vars=vars)
		elif spec == IndexerSpec.Tags.slice_array:
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**vars, 'var_type': var_type})
		elif spec == IndexerSpec.Tags.slice_string:
			return self.view.render(f'{node.classification}/{spec.name}', vars=vars)
		elif spec == IndexerSpec.Tags.tuple:
			return self.view.render(f'{node.classification}/{spec.name}', vars={**vars, 'receiver': receiver, 'key': keys[0]})
		else:
			return self.view.render(f'{node.classification}/default', vars={**vars, 'receiver': receiver, 'key': keys[0]})

	def analyze_indexer_spec(self, node: defs.Indexer) -> 'tuple[IndexerSpec.Tags, IReflection | None]':
		receiver_symbol = Defer.new(lambda: self.reflections.type_of(node.receiver).impl(refs.Object).actualize())
		symbol = Defer.new(lambda: self.reflections.type_of(node).impl(refs.Object))
		if node.sliced:
			if receiver_symbol.type_is(str):
				return IndexerSpec.Tags.slice_string, receiver_symbol
			else:
				return IndexerSpec.Tags.slice_array, receiver_symbol
		elif symbol.type_is(type):
			return IndexerSpec.Tags.klass, symbol.actualize()
		elif receiver_symbol.type_is(tuple):
			return IndexerSpec.Tags.tuple, None
		elif self.cvars.is_addr_p(self.cvars.var_name_from(receiver_symbol)):
			return IndexerSpec.Tags.cvar, None
		else:
			return IndexerSpec.Tags.otherwise, None

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: str) -> str:
		prop_symbol = self.reflections.type_of(node.receiver).impl(refs.Object).prop_of(node.prop)
		type_name = self.to_domain_name_by_class(prop_symbol.types)
		return self.view.render(f'type/{node.classification}', vars={'receiver': receiver, 'type_name': type_name})

	def on_var_of_type(self, node: defs.VarOfType) -> str:
		symbol = self.reflections.type_of(node)
		# ノードが戻り値の型であり、且つSelfの場合、所属クラスのシンボルに変換 FIXME 場当たり的、且つ不完全なため修正を検討
		if isinstance(node.parent, (defs.Method, defs.ClassMethod)) and isinstance(symbol.types, defs.TemplateClass) and symbol.types.domain_name == Self.__name__:
			symbol = self.reflections.resolve(node.parent.class_types)

		type_name = self.to_domain_name_by_class(symbol.types)
		if isinstance(symbol.types, defs.TemplateClass):
			return self.view.render(f'type/template', vars={'type_name': type_name, 'definition_type': symbol.types.definition_type.tokens})
		else:
			return self.view.render(f'type/{node.classification}', vars={'type_name': type_name})

	def on_literal_type(self, node: defs.LiteralType) -> str:
		symbol = self.reflections.type_of(node)
		type_name = self.to_domain_name_by_class(symbol.types)
		return self.view.render(f'type/{node.classification}', vars={'type_name': type_name})

	def on_list_type(self, node: defs.ListType, type_name: str, value_type: str) -> str:
		return self.view.render(f'type/{node.classification}', vars={'type_name': type_name, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(f'type/{node.classification}', vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_callable_type(self, node: defs.CallableType, type_name: str, parameters: list[str], return_type: str) -> str:
		"""
		Note:
			```
			### PluckMethodのシグネチャー
			* `Callable[[T, *T_Args], None]`
			```
		"""
		spec = node.classification
		if len(parameters) >= 2:
			second_type = self.reflections.type_of(node.parameters[1])
			if isinstance(second_type.types, defs.TemplateClass) and second_type.types.definition_type.type_name.tokens == TypeVarTuple.__name__:
				spec = 'pluck_method'

		return self.view.render(f'type/{spec}', vars={'type_name': type_name, 'parameters': parameters, 'return_type': return_type})

	def on_custom_type(self, node: defs.CustomType, type_name: str, sub_types: list[str]) -> str:
		# XXX @see semantics.reflection.helper.naming.ClassShorthandNaming.domain_name
		return self.view.render('type_py2cpp', vars={'var_type': f'{type_name}<{", ".join(sub_types)}>'})

	def on_literal_dict_type(self, node: defs.LiteralDictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(f'type/{node.classification}', vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_union_type(self, node: defs.UnionType, or_types: list[str]) -> str:
		"""Note: XXX C++でUnion型の表現は不可能。期待値を仮定するのであればプライマリー型以外に無いので先頭要素のみ返却"""
		return or_types[0]

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		is_statement = node.parent.is_a(defs.Block, defs.Entrypoint)
		spec, prop, context = self.analyze_func_call_spec(node)
		func_call_vars = {'calls': calls, 'arguments': arguments, 'is_statement': is_statement}
		if spec == FuncCallSpec.Tags.c_include:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.c_macro:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.c_pragma:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.c_func_invoke:
			receiver_raw = Defer.new(lambda: self.reflections.type_of(node.arguments[0]).impl(refs.Object).actualize())
			operator = '->' if node.arguments[0].value.is_a(defs.ThisRef) or self.cvars.is_addr(self.cvars.var_name_from(receiver_raw)) else '.'
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'operator': operator})
		elif spec == FuncCallSpec.Tags.c_func_ref:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.c_type_expr:
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.copy_constructor:
			# 期待値: 'receiver.__py_copy__'
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.generic_call:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cast_char:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cast_enum:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cast_list:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cast_bin_to_bin:
			from_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'from_type': from_type})
		elif spec == FuncCallSpec.Tags.cast_bin_to_str:
			from_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'from_type': from_type})
		elif spec == FuncCallSpec.Tags.cast_str_to_bin:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cast_str_to_str:
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.len:
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.print:
			# XXX 愚直に対応すると実引数の型推論のコストが高く、その割に出力メッセージの柔軟性が下がりメリットが薄いため、関数名の置き換えのみを行う簡易的な対応とする
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.str and prop == str.format.__name__:
			is_literal = node.calls.as_a(defs.Relay).receiver.is_a(defs.String)
			receiver, operator = PatternParser.break_relay(calls)
			to_tags = {int.__name__: '%d', float.__name__: '%f', bool.__name__: '%d', str.__name__: '%s', CP.__name__: '%p', CWP.__name__: '%p'}
			formatters: list[dict[str, Any]] = []
			for argument in node.arguments:
				arg_symbol = self.reflections.type_of(argument)
				formatters.append({'label': argument.label.tokens, 'tag': to_tags.get(arg_symbol.types.domain_name, '%s'), 'var_type': arg_symbol.types.domain_name, 'is_literal': argument.value.is_a(defs.Literal)})

			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'is_literal': is_literal, 'formatters': formatters})
		elif spec == FuncCallSpec.Tags.str:
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == FuncCallSpec.Tags.list and prop == list.copy.__name__:
			# 期待値: 'receiver.copy'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.list and prop == list.pop.__name__:
			# 期待値: 'receiver.pop'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.list and prop == list.insert.__name__:
			# 期待値: 'receiver.insert'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == FuncCallSpec.Tags.list and prop == list.extend.__name__:
			# 期待値: 'receiver.extend'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == FuncCallSpec.Tags.list and prop == list.sort.__name__ and len(arguments) > 0:
			# 期待値: 'receiver.sort([]({entry_type} entry) -> Any { return entry; })'
			entry_type, entry_name, entry_value = PatternParser.break_list_sort_key(arguments[0])
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'entry_type': entry_type, 'entry_name': entry_name, 'entry_value': entry_value})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.copy.__name__:
			# 期待値: 'receiver.copy'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.get.__name__:
			# 期待値: 'receiver.get'
			receiver, operator = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.keys.__name__:
			# 期待値: 'receiver.keys'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.items.__name__:
			# 期待値: 'receiver.items'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.pop.__name__:
			# 期待値: 'receiver.pop'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.dict and prop == dict.values.__name__:
			# 期待値: 'receiver.values'
			receiver, operator = PatternParser.break_relay(calls)
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}_{prop}', vars={**func_call_vars, 'receiver': receiver, 'operator': operator, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.cvar_as_a:
			# 期待値: receiver.as_a(A)
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.cvar_copy:
			# 期待値: cref_to.copy(cref_via)
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.cvar_down:
			# 期待値: receiver.down(A)
			receiver, _ = PatternParser.break_relay(calls)
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver})
		elif spec == FuncCallSpec.Tags.cvar_new_p:
			# 期待値: CP.new(A(a, b, c))
			return self.view.render(f'{node.classification}/{spec.name}', vars=func_call_vars)
		elif spec == FuncCallSpec.Tags.cvar_new_sp_list:
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

			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		elif spec == FuncCallSpec.Tags.cvar_new_sp:
			# 期待値: CSP.new(A(a, b, c))
			var_type, initializer = PatternParser.pluck_cvar_new(arguments[0])
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'var_type': var_type, 'initializer': initializer})
		elif spec == FuncCallSpec.Tags.cvar_sp_empty:
			# 期待値: CSP[A].empty()
			var_type = self.to_accessible_name(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == FuncCallSpec.Tags.cvar_to:
			# 期待値: CP(a)
			cvar_key = self.cvars.var_name_from(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'cvar_type': cvar_key})
		elif spec == FuncCallSpec.Tags.cvar_to_addr_hex:
			# 期待値: receiver.to_addr_hex()
			receiver, _ = PatternParser.break_relay(calls)
			cvar_key = self.cvars.var_name_from(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver, 'is_addr': self.cvars.is_addr(cvar_key)})
		elif spec == FuncCallSpec.Tags.cvar_to_addr_id:
			# 期待値: receiver.to_addr_id()
			receiver, _ = PatternParser.break_relay(calls)
			cvar_key = self.cvars.var_name_from(cast(IReflection, context))
			return self.view.render(f'{node.classification}/{spec.name}', vars={**func_call_vars, 'receiver': receiver, 'is_addr': self.cvars.is_addr(cvar_key)})
		else:
			return self.view.render(f'{node.classification}/default', vars=func_call_vars)

	def analyze_func_call_spec(self, node: defs.FuncCall) -> 'tuple[FuncCallSpec.Tags, str, IReflection | None]':
		"""Note: XXX callsは別名になる可能性があるため、ノードから取得したcallsを使用する"""
		calls_raw = Defer.new(lambda: self.reflections.type_of(node.calls).impl(refs.Object).actualize())
		if isinstance(node.calls, defs.Var):
			calls = node.calls.tokens
			if calls == c_pragma.__name__:
				return FuncCallSpec.Tags.c_pragma, '', None
			elif calls == c_include.__name__:
				return FuncCallSpec.Tags.c_include, '', None
			elif calls == c_macro.__name__:
				return FuncCallSpec.Tags.c_macro, '', None
			elif calls == c_func_invoke.__name__:
				return FuncCallSpec.Tags.c_func_invoke, '', None
			elif calls == c_func_ref.__name__:
				return FuncCallSpec.Tags.c_func_ref, '', None
			if calls == isinstance.__name__:
				return FuncCallSpec.Tags.c_type_expr, '', self.reflections.type_of(node.arguments[0])
			elif calls == len.__name__:
				return FuncCallSpec.Tags.len, '', self.reflections.type_of(node.arguments[0])
			elif calls == print.__name__:
				return FuncCallSpec.Tags.print, '', None
			elif calls == char.__name__:
				return FuncCallSpec.Tags.cast_char, '', None
			elif calls == list.__name__:
				return FuncCallSpec.Tags.cast_list, '', None
			elif len(node.arguments) > 0 and calls in FuncCallSpec.convertion_scalars:
				from_raw = self.reflections.type_of(node.arguments[0]).impl(refs.Object)
				to_raw = self.reflections.type_of(node.calls).impl(refs.Object).actualize('type')
				if from_raw.type_is(str) and to_raw.type_is(str):
					return FuncCallSpec.Tags.cast_str_to_str, '', None
				elif from_raw.type_is(str):
					return FuncCallSpec.Tags.cast_str_to_bin, '', None
				elif to_raw.type_is(str):
					return FuncCallSpec.Tags.cast_bin_to_str, '', from_raw
				else:
					return FuncCallSpec.Tags.cast_bin_to_bin, '', from_raw
			elif not self.cvars.is_entity(self.cvars.var_name_from(calls_raw)):
				# XXX AltClassを考慮するとRelay側も対応が必要で片手落ち
				return FuncCallSpec.Tags.cvar_to, '', calls_raw
		elif isinstance(node.calls, defs.Relay):
			prop = node.calls.prop.tokens
			if prop in FuncCallSpec.list_and_dict_methods:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object)
				if prop in FuncCallSpec.list_methods and receiver_raw.type_is(list):
					return FuncCallSpec.Tags.list, prop, receiver_raw.attrs[0]
				elif receiver_raw.type_is(dict) and node.parent.is_a(defs.ForIn):
					# XXX for/comprehensionにより、レシーバー自体がイテレーターとして評価されるため、通常の関数コールとして処理
					return FuncCallSpec.Tags.otherwise, '', None
				elif receiver_raw.type_is(dict):
					key_attr, value_attr = receiver_raw.attrs
					prop_to_context = {dict.pop.__name__: value_attr, dict.keys.__name__: key_attr, dict.values.__name__: value_attr, dict.items.__name__: receiver_raw, dict.get.__name__: value_attr, dict.copy.__name__: receiver_raw}
					return FuncCallSpec.Tags.dict, prop, prop_to_context[prop]
			elif prop in FuncCallSpec.str_methods:
				if node.calls.receiver.is_a(defs.String):
					return FuncCallSpec.Tags.str, prop, None
				elif self.reflections.type_of(node.calls.receiver).impl(refs.Object).type_is(str):
					return FuncCallSpec.Tags.str, prop, None
			elif prop == PythonClassOperations.copy_constructor:
				return FuncCallSpec.Tags.copy_constructor, '', None
			elif prop == CVars.Verbs.CopyProxy.value:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if self.cvars.is_raw_ref(cvar_key):
					return FuncCallSpec.Tags.cvar_copy, '', None
			elif prop in [CVars.Verbs.Down.value, CVars.Verbs.AsA.value]:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if self.cvars.is_addr_p(cvar_key):
					spec = FuncCallSpec.Tags.cvar_down if prop == CVars.Verbs.Down.value else FuncCallSpec.Tags.cvar_as_a
					return spec, '', None
			elif prop == CVars.Verbs.Emtpy.value and isinstance(node.calls.receiver, defs.Indexer):
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if self.cvars.is_addr_sp(cvar_key):
					# 期待値: CSP[A] | None
					entity_raw = self.reflections.type_of(node).attrs[0].attrs[0]
					return FuncCallSpec.Tags.cvar_sp_empty, '', entity_raw
			elif prop == CVars.Verbs.New.value and isinstance(node.calls.receiver, defs.Var):
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if self.cvars.is_addr_p(cvar_key):
					return FuncCallSpec.Tags.cvar_new_p, '', None
				elif self.cvars.is_addr_sp(cvar_key):
					new_type_raw = self.reflections.type_of(node.arguments[0]).impl(refs.Object)
					if new_type_raw.type_is(list):
						return FuncCallSpec.Tags.cvar_new_sp_list, '', new_type_raw

					return FuncCallSpec.Tags.cvar_new_sp, '', None
			elif prop == CVars.Verbs.ToAddrHex.value:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if not self.cvars.is_entity(cvar_key):
					return FuncCallSpec.Tags.cvar_to_addr_hex, '', receiver_raw
			elif prop == CVars.Verbs.ToAddrId.value:
				receiver_raw = self.reflections.type_of(node.calls.receiver).impl(refs.Object).actualize()
				cvar_key = self.cvars.var_name_from(receiver_raw)
				if not self.cvars.is_entity(cvar_key):
					return FuncCallSpec.Tags.cvar_to_addr_id, '', receiver_raw

		if isinstance(node.calls, (defs.Relay, defs.Var)):
			if len(node.arguments) > 0 and node.arguments[0].value.is_a(defs.Reference):
				primary_arg_raw = self.reflections.type_of(node.arguments[0])
				if primary_arg_raw.impl(refs.Object).type_is(type):
					return FuncCallSpec.Tags.generic_call, '', None

			if calls_raw.types.is_a(defs.Enum):
				return FuncCallSpec.Tags.cast_enum, '', None

		return FuncCallSpec.Tags.otherwise, '', None

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		parent_symbol = self.reflections.type_of(node)
		return self.to_accessible_name(parent_symbol)

	def on_for_in(self, node: defs.ForIn, iterates: str) -> str:
		return iterates

	def on_comp_for(self, node: defs.CompFor, symbols: list[str], for_in: str) -> str:
		# XXX is_const/is_addr_pの対応に一貫性が無い。包括的な対応を検討
		for_in_symbol = Defer.new(lambda: self.reflections.type_of(node.for_in).impl(refs.Object).actualize())
		is_const = self.cvars.is_const(self.cvars.var_name_from(for_in_symbol)) if len(symbols) == 1 else False
		is_addr_p = self.cvars.is_addr_p(self.cvars.var_name_from(for_in_symbol)) if len(symbols) == 1 else False

		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Var) and node.iterates.calls.tokens in [range.__name__, enumerate.__name__]:
			spec = node.iterates.calls.tokens
			return self.view.render(f'comp/{node.classification}_{spec}', vars={'symbols': symbols, 'iterates': for_in, 'is_const': is_const, 'is_addr_p': is_addr_p})
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Relay) \
			and node.iterates.calls.prop.tokens in FuncCallSpec.dict_iter_methods \
			and self.reflections.type_of(node.iterates.calls.receiver).impl(refs.Object).actualize().type_is(dict):
			# 期待値: 'iterates.items()'
			receiver, operator, _ = PatternParser.break_dict_iterator(for_in)
			method_name = node.iterates.calls.prop.tokens
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
		return self.view.render('operation/unary_operator', vars={'operator': operator, 'value': value})

	def on_not_compare(self, node: defs.NotCompare, operator: str, value: str) -> str:
		return self.view.render('operation/unary_operator', vars={'operator': '!', 'value': value})

	def on_or_compare(self, node: defs.OrCompare, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_and_compare(self, node: defs.AndCompare, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_comparison(self, node: defs.Comparison, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_or_bitwise(self, node: defs.OrBitwise, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_xor_bitwise(self, node: defs.XorBitwise, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_and_bitwise(self, node: defs.AndBitwise, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_sum(self, node: defs.Sum, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def on_term(self, node: defs.Term, elements: list[str]) -> str:
		return self.proc_binary_operation(node, elements)

	def proc_binary_operation(self, node: defs.BinaryOperator, elements: list[str]) -> str:
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
			return self.proc_binary_operation_fill_list(node, default_raw, size_raw, default, size)
		else:
			return self.proc_binary_operation_expression(node, primary_raw, secondary_raws, primary, operators, secondaries)

	def proc_binary_operation_fill_list(self, node: defs.BinaryOperator, default_raw: IReflection, size_raw: IReflection, default: str, size: str) -> str:
		value_type = self.to_accessible_name(default_raw.attrs[0])
		default_is_list = default_raw.node.is_a(defs.List)
		return self.view.render('operation/binary_fill_list', vars={'value_type': value_type, 'default': default, 'size': size, 'default_is_list': default_is_list})

	def proc_binary_operation_expression(self, node: defs.BinaryOperator, left_raw: IReflection, right_raws: list[IReflection], left: str, operators: list[str], rights: list[str]) -> str:
		primary = left
		primary_raw = left_raw
		for index, right_raw in enumerate(right_raws):
			operator = operators[index]
			secondary = rights[index]
			if operator in ['in', 'not.in']:
				primary = self.view.render('operation/binary_in', vars={'left': primary, 'operator': operator, 'right': secondary, 'right_is_dict': right_raw.impl(refs.Object).type_is(dict)})
			else:
				primary = self.view.render('operation/binary_operator', vars={'left': primary, 'operator': operator, 'right': secondary, 'left_var_type': self.to_domain_name(primary_raw), 'right_var_type': self.to_domain_name(right_raw)})

			primary_raw = right_raw

		return primary

	def on_ternary_operator(self, node: defs.TernaryOperator, primary: str, condition: str, secondary: str) -> str:
		return self.view.render(f'operation/{node.classification}', vars={'primary': primary, 'condition': condition, 'secondary': secondary})

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
		raise Errors.NotSupported(node, 'Denied spread expression')

	def on_lambda(self, node: defs.Lambda, symbols: str, expression: str) -> str:
		params: dict[str, str] = {}
		for index, param in enumerate(node.symbols):
			param_raw = self.reflections.type_of(param)
			params[symbols[index]] = self.to_accessible_name(param_raw)

		expression_raw = self.reflections.type_of(node.expression)
		return_type = self.to_accessible_name(expression_raw)
		return self.view.render(f'{node.classification}/default', vars={'params': params, 'expression': expression, 'return_type': return_type, 'binds': self.make_lambda_binds(node)})

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


class IndexerSpec:
	"""マッピング情報(Indexer)"""

	class Tags(Enum):
		"""タグ種別"""
		otherwise = -1
		klass = 0
		cvar = 1
		slice_array = 2
		slice_string = 3
		tuple = 4


class FuncCallSpec:
	"""マッピング情報(FuncCall)"""

	class Tags(Enum):
		"""タグ種別"""
		otherwise = -1
		# cpp
		c_include = 0
		c_macro = 1
		c_pragma = 2
		c_func_invoke = 3
		c_func_ref = 4
		c_type_expr = 5
		copy_constructor = 6
		# generic
		generic_call = 100
		# cast
		cast_char = 200
		cast_enum = 201
		cast_list = 202
		cast_bin_to_bin = 203
		cast_bin_to_str = 204
		cast_str_to_bin = 205
		cast_str_to_str = 206
		# stdlib
		len = 300
		print = 301
		str = 302
		list = 303
		dict = 304
		# cvar
		cvar_as_a = 400
		cvar_copy = 401
		cvar_down = 402
		cvar_new_p = 403
		cvar_new_sp_list = 404
		cvar_new_sp = 405
		cvar_sp_empty = 406
		cvar_to = 407
		cvar_to_addr_hex = 408
		cvar_to_addr_id = 409

	convertion_scalars: ClassVar[list[str]] = [
		bool.__name__,
		int.__name__,
		float.__name__,
		str.__name__,
		byte.__name__,
		uint32.__name__,
		int64.__name__,
		uint64.__name__,
		double.__name__,
	]
	list_methods: ClassVar[list[str]] = [
		list.pop.__name__,
		list.insert.__name__,
		list.extend.__name__,
		list.copy.__name__,
		list.sort.__name__,
	]
	dict_iter_methods: ClassVar[list[str]] = [
		dict.items.__name__,
		dict.keys.__name__,
		dict.values.__name__,
	]
	list_and_dict_methods: ClassVar[list[str]] = [
		*list_methods,
		*dict_iter_methods,
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

	RelayPattern: ClassVar[re.Pattern] = re.compile(r'(.+)(->|::|\.)\w+$')
	ListSortKeyPattern: ClassVar[re.Pattern[str]] = re.compile(r'\[[^(]*\]\((.+) ([\w\d]+)\)[^{]+\{ return ([^;]+); \}')
	DictIteratorPattern: ClassVar[re.Pattern] = re.compile(r'(.+)(->|\.)(\w+)\(\)$')
	SuperCallPattern: ClassVar[re.Pattern] = re.compile(r'([\w\d]+)::__init__\((.*)\);$')
	DeclClassVarNamePattern: ClassVar[re.Pattern] = re.compile(r'\s+([\w\d_]+)\s+=')
	MoveDeclRightPattern: ClassVar[re.Pattern] = re.compile(r'=\s*([^;]+);$')
	InitDeclRightPattern: ClassVar[re.Pattern] = re.compile(r'({[^;]*});$')
	CVarRelaySubPattern: ClassVar[re.Pattern] = re.compile(rf'(->|::|\.){CVars.Verbs.On.value}\(\)$')
	CVarToSubPattern: ClassVar[re.Pattern] = re.compile(rf'(->|::|\.)({"|".join(CVars.Casts.values())})\(\)$')

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
	def break_list_sort_key(cls, arg: str) -> tuple[str, str, str]:
		"""配列のキーソートコールから各要素に分解

		Args:
			arg: 文字列
		Returns:
			(エントリーの型, 引数の名前, 比較対象の式)
		Note:
			```
			### 期待値
			'[](Entry entry) -> Any { return entry.value; }' -> ('Entry', 'entry', 'entry.value')
			```
		"""
		return cast(re.Match, re.fullmatch(cls.ListSortKeyPattern, arg)).group(1, 2, 3)

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
	def break_super_call(cls, func_call: str) -> tuple[str, str]:
		"""関数コール(super)から親クラス名と引数リストに分解

		Args:
			func_call: 文字列
		Returns:
			(クラス, 引数リスト)
		Note:
			```
			### 期待値
			'NS::Class::__init__(arguments...);' -> ('Class', 'arguments...')
			```
		"""
		return cast(re.Match, cls.SuperCallPattern.search(func_call)).group(1, 2)

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
	def pluck_cvar_new(cls, argument: str) -> tuple[str, str]:
		"""C++型変数のメモリー生成関数コールを分解

		Args:
			argument: 文字列
		Returns:
			(レシーバー, 引数)
		Note:
			```
			### 期待値
			'Class(arguments...)' -> ('Class', 'arguments...')
			```
		"""
		return BlockParser.break_last_block(argument, '()')

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
