import re
from typing import cast

from rogw.tranp.analyze.procedure import Procedure
import rogw.tranp.analyze.reflection as reflection
from rogw.tranp.analyze.symbol import SymbolRaw
from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.ast.dsn import DSN
import rogw.tranp.compatible.cpp.object as cpp
import rogw.tranp.compatible.python.embed as __alias__
from rogw.tranp.errors import LogicError
from rogw.tranp.implements.cpp.analyze.cvars import CVars
from rogw.tranp.lang.implementation import injectable
import rogw.tranp.node.definition as defs
from rogw.tranp.node.definition.statement_compound import ClassSymbolMaker
from rogw.tranp.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.view.render import Renderer


class Py2Cpp:
	"""Python -> C++のトランスパイラー"""

	@injectable
	def __init__(self, symbols: Symbols, render: Renderer, options: TranslatorOptions) -> None:
		"""インスタンスを生成

		Args:
			symbols (Symbols): シンボルリゾルバー @inject
			render (Renderer): ソースレンダー @inject
			options (TranslatorOptions): 実行オプション @inject
		"""
		self.symbols = symbols
		self.view = render
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

	def translate(self, root: Node) -> str:
		"""起点のノードからASTを再帰的に解析し、C++にトランスパイル

		Args:
			root (Node): 起点のノード
		Returns:
			str: C++のソースコード
		"""
		return self.__procedure.exec(root)

	def to_symbol_path(self, raw: SymbolRaw) -> str:
		"""名前空間によるシンボルの参照名を取得 (MoveAssignなど、型を補完する際に利用)

		Args:
			raw (SymbolRaw): シンボル
		Returns:
			str: C++用のシンボルの完全参照名
		Note:
			# 生成例
			'Class' -> 'NS::Class'
			'dict<A, B>' -> 'dict<NS::A, NS::B>'
		"""
		unpacked_raw = CVars.unpack_with_nullable(self.symbols, raw)
		return DSN.join(*DSN.elements(unpacked_raw.make_shorthand(use_alias=True, path_method='namespace')), delimiter='::')

	def to_symbol_name(self, var_type_raw: SymbolRaw) -> str:
		"""明示されたタイプよりシンボルの参照名を取得 (主にAnnoAssignで利用)

		Args:
			var_type_raw (SymbolRaw): シンボル
		Returns:
			str: C++用のシンボルの参照名
		Note:
			# 生成例
			'Union<Class[CP], None>' -> 'Class[CP]'
		"""
		unpacked_raw = CVars.unpack_with_nullable(self.symbols, var_type_raw)
		return unpacked_raw.make_shorthand(use_alias=True)

	def accepted_cvar_value(self, accept_raw: SymbolRaw, value_node: Node, value_raw: SymbolRaw, value_str: str, declared: bool = False) -> str:
		"""受け入れ出来る形式に変換(代入の右辺値/実引数/返却値)

		Args:
			accept_raw (SymbolRaw): シンボル(受け入れ側)
			value_raw (SymbolRaw): シンボル(入力側)
			value_str (str): 入力値
			declared (bool): True = 変数宣言時
		Returns:
			str: 変換後の入力値
		Note:
			# 期待する書式
			* `Class a = ${value_str};`
			* `func(${value_str}, ...);`
			* `return ${value_str};`
		"""
		value_on_new = isinstance(value_node, defs.FuncCall) and self.symbols.type_of(value_node.calls).types.is_a(defs.Class)
		move = CVars.analyze_move(self.symbols, accept_raw, value_raw, value_on_new, declared)
		if move == CVars.Moves.Deny:
			raise LogicError(f'Unacceptable value move. accept: {str(accept_raw)}, value: {str(value_raw)}, value_on_new: {value_on_new}, declared: {declared}')

		return self.to_cvar_value(move, value_str)

	def iterable_cvar_value(self, value_node: Node, value_raw: SymbolRaw, value_str: str, declared: bool = False) -> str:
		"""受け入れ出来る形式に変換(分割代入の右辺値)

		Args:
			value_raw (SymbolRaw): シンボル(入力側)
			value_str (str): 入力値
			declared (bool): True = 変数宣言時
		Returns:
			str: 変換後の入力値
		Note:
			# 期待する書式
			* `auto& [dest_a, dest_b, ...] = ${value_str};`
			* `for (auto& [dest_a, dest_b, ...] : ${value_str}) { /** some */ }`
		"""
		value_on_new = isinstance(value_node, defs.FuncCall) and self.symbols.type_of(value_node.calls).types.is_a(defs.Class)
		move = CVars.move_by(cpp.CRef.__name__, CVars.key_from(self.symbols, value_raw), value_on_new, declared)
		if move == CVars.Moves.Deny:
			raise LogicError(f'Unacceptable value move. value: {str(value_raw)}, value_on_new: {value_on_new}, declared: {declared}')

		return self.to_cvar_value(move, value_str)

	def calculable_cvar_value(self, value_raw: SymbolRaw, value_str: str) -> str:
		"""受け入れ出来る形式に変換(1,2項演算用)

		Args:
			value_raw (SymbolRaw): 値のシンボル
			value_str (str): 入力値
		Returns:
			str: 変換後の入力値
		Note:
			# 期待する書式
			* `not_v = !${value_str};`
			* `add_v = left + ${value_str};`
		"""
		if CVars.is_addr(CVars.key_from(self.symbols, value_raw)):
			return self.to_cvar_value(CVars.Moves.ToActual, value_str)

		return value_str

	def to_cvar_value(self, move: 'CVars.Moves', value_str: str) -> str:
		"""C++変数型を考慮した変数移動操作の値に変換

		Args:
			move (Moves): C++変数型の移動操作
			value_str (str): 入力値
		Returns:
			str: 変換後の入力値
		"""
		if move == CVars.Moves.MakeSp:
			# XXX 関数名(クラス名)と引数を分離。必ず取得できるので警告を抑制(期待値: `Class(a, b, c)`)
			matches = cast(re.Match, re.fullmatch(r'([^(]+)\((.*)\)', value_str))
			return self.view.render('cvar_move', vars={'move': move.name, 'var_type': matches[1], 'arguments': matches[2]})
		else:
			return self.view.render('cvar_move', vars={'move': move.name, 'value': value_str})

	def unpack_function_template_types(self, node: defs.Function) -> list[str]:
		"""ファンクションのテンプレート型名をアンパック

		Args:
			node (Function): ファンクションノード
		Returns:
			list[str]: テンプレート型名リスト
		"""
		function_raw = self.symbols.type_of(node)
		function_ref = reflection.Builder(function_raw) \
			.case(reflection.Method).schema(lambda: {'klass': function_raw.attrs[0], 'parameters': function_raw.attrs[1:-1], 'returns': function_raw.attrs[-1]}) \
			.other_case().schema(lambda: {'parameters': function_raw.attrs[1:-1], 'returns': function_raw.attrs[-1]}) \
			.build(reflection.Function)
		return [types.domain_name for types in function_ref.templates()]

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		return self.view.render('block', vars={'statements': statements})

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
		if isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Variable) and node.iterates.calls.tokens == range.__name__:
			return self.proc_for_range(node, symbols, for_in, statements)
		elif isinstance(node.iterates, defs.FuncCall) and isinstance(node.iterates.calls, defs.Variable) and node.iterates.calls.tokens == enumerate.__name__:
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
		var_type = self.to_symbol_path(self.symbols.type_of(node.for_in).attrs[1])
		return self.view.render(f'{node.classification}_enumerate', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements, 'id': node.id, 'var_type': var_type})

	def proc_for_dict_items(self, node: defs.For, symbols: list[str], for_in: str, statements: list[str]) -> str:
		iterates = cast(re.Match, re.fullmatch(r'(.+)\.items\(\)', for_in))[1]
		return self.view.render(f'{node.classification}_dict_items', vars={'symbols': symbols, 'iterates': iterates, 'statements': statements})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements, 'catches': catches})

	def on_comp_for(self, node: defs.CompFor, symbols: list[str], for_in: str) -> str:
		return self.view.render(node.classification, vars={'symbols': symbols, 'iterates': for_in})

	def on_list_comp(self, node: defs.ListComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.symbols.type_of(node.projection)
		projection_type = self.to_symbol_path(projection_type_raw)
		comp_vars = {'projection': projection, 'comp_for': fors[0], 'condition': condition, 'projection_types': [projection_type], 'binded_this': node.binded_this}
		return self.view.render(node.classification, vars=comp_vars)

	def on_dict_comp(self, node: defs.DictComp, projection: str, fors: list[str], condition: str) -> str:
		projection_type_raw = self.symbols.type_of(node.projection)
		projection_type_key = self.to_symbol_path(projection_type_raw.attrs[0])
		projection_type_value = self.to_symbol_path(projection_type_raw.attrs[1])
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

		class_name = ClassSymbolMaker.domain_name(node.class_types, use_alias=True)
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
			var_type_raw = self.symbols.type_of(this_var.declare.as_a(defs.AnnoAssign).var_type)
			var_type = self.to_symbol_name(var_type_raw)
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
		receiver_raw = self.symbols.type_of(node.receivers[0])
		value_raw = self.symbols.type_of(node.value)
		declared = receiver_raw.decl.declare == node
		var_type = self.to_symbol_path(value_raw) if declared else ''
		accepted_value = self.accepted_cvar_value(receiver_raw, node.value, self.symbols.type_of(node.value), value, declared=declared)
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': accepted_value})

	def proc_move_assign_unpack(self, node: defs.MoveAssign, receivers: list[str], value: str) -> str:
		accepted_value = self.iterable_cvar_value(node.value, self.symbols.type_of(node.value), value, declared=True)
		return self.view.render(f'{node.classification}_unpack', vars={'receivers': receivers, 'value': accepted_value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		accepted_value = self.accepted_cvar_value(self.symbols.type_of(node.receiver), node.value, self.symbols.type_of(node.value), value, declared=True)
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': accepted_value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, operator: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'operator': operator, 'value': value})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		accepted_value = self.accepted_cvar_value(self.symbols.type_of(node.function).attrs[-1], node.return_value, self.symbols.type_of(node.return_value), return_value)
		return self.view.render(node.classification, vars={'return_value': accepted_value})

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(node.classification, vars={'throws': throws, 'via': via})

	def on_pass(self, node: defs.Pass) -> None:
		pass

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_import(self, node: defs.Import, import_symbols: list[str]) -> str:
		module_path = node.import_path.tokens
		text = self.view.render(node.classification, vars={'module_path': module_path})
		return text if module_path.startswith('example.FW') else f'// {text}'

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
		return ClassSymbolMaker.domain_name(node.class_types.as_a(defs.ClassDef), use_alias=True)

	def on_import_name(self, node: defs.ImportName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		receiver_symbol = self.symbols.type_of(node.receiver)
		prop_symbol = self.symbols.type_of_property(receiver_symbol.types, node.prop)
		prop = node.prop.tokens
		if isinstance(prop_symbol.decl, defs.ClassDef):
			prop = ClassSymbolMaker.domain_name(prop_symbol.types, use_alias=True)

		def is_cvar_receiver() -> bool:
			return len(receiver_symbol.attrs) > 0 and receiver_symbol.attrs[0].types.symbol.tokens in CVars.keys()

		def is_this_var() -> bool:
			return node.receiver.is_a(defs.ThisRef)

		def is_static_access() -> bool:
			is_class_alias = isinstance(node.receiver, (defs.ClassRef, defs.Super))
			is_class_access = receiver_symbol.decl.is_a(defs.ClassDef)
			return is_class_alias or is_class_access

		if is_cvar_receiver():
			cvar_type = receiver_symbol.attrs[0].types.symbol.tokens
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': cvar_type, 'prop': prop})
		elif is_this_var():
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'arrow', 'prop': prop})
		elif is_static_access():
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'static', 'prop': prop})
		else:
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'dot', 'prop': prop})

	def on_class_ref(self, node: defs.ClassRef) -> str:
		return node.class_symbol.tokens

	def on_this_ref(self, node: defs.ThisRef) -> str:
		return 'this'

	def on_argument_label(self, node: defs.ArgumentLabel) -> str:
		return node.tokens

	def on_variable(self, node: defs.Variable) -> str:
		symbol = self.symbols.type_of(node)
		if isinstance(symbol.decl, defs.ClassDef):
			return ClassSymbolMaker.domain_name(symbol.types, use_alias=True)
		else:
			return node.tokens

	def on_indexer(self, node: defs.Indexer, receiver: str, key: str) -> str:
		if key in CVars.keys():
			# XXX 互換用の型は不要なので除外
			return receiver
		else:
			return f'{receiver}[{key}]'

	def on_relay_of_type(self, node: defs.RelayOfType, receiver: str) -> str:
		receiver_symbol = self.symbols.type_of(node.receiver)
		prop_symbol = self.symbols.type_of_property(receiver_symbol.types, node.prop)
		type_name = ClassSymbolMaker.domain_name(prop_symbol.types, use_alias=True)
		return self.view.render(node.classification, vars={'receiver': receiver, 'type_name': type_name})

	def on_var_of_type(self, node: defs.VarOfType) -> str:
		symbol = self.symbols.type_of(node)
		type_name = ClassSymbolMaker.domain_name(symbol.types, use_alias=True)
		return self.view.render(node.classification, vars={'type_name': type_name})

	def on_list_type(self, node: defs.ListType, type_name: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_callable_type(self, node: defs.CallableType, type_name: str, parameters: list[str], return_type: str) -> str:
		raise NotImplementedError(f'Not supported CallableType. symbol: {node.fullyname}')

	def on_custom_type(self, node: defs.CustomType, type_name: str, template_types: list[str]) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'cvar_type': template_types[0], 'cmutable': template_types[1] if len(template_types) == 2 else ''})

	def on_union_type(self, node: defs.UnionType, or_types: list[str]) -> str:
		"""
		Note:
			Union型はNullableのみ許可 (変換例: 'Class[CP] | None' -> 'Class*'
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
		is_addr_p = isinstance(var_type_node, defs.CustomType) and CVars.is_addr_p(var_type_node.template_types[0].type_name.tokens)
		if not is_addr_p:
			raise LogicError(f'Unexpected UnionType. with not pointer. symbol: {node.fullyname}, var_type: {var_type_node}')

		return or_types[var_type_index]

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		accepted_arguments = self.accepted_arguments(node, arguments)
		is_statement = node.parent.is_a(defs.Block)
		spec, context = self.analyze_func_call_spec(node, calls)
		func_call_vars = {'calls': calls, 'arguments': accepted_arguments, 'is_statement': is_statement}
		if spec == 'directive':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'len':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'print':
			# XXX 愚直に対応すると実引数の型推論がかなり重く、その割に出力メッセージの柔軟性が低くメリットが薄いため、関数名の置き換えのみを行う簡易的な対応とする
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'new_list':
			return self.view.render(f'{node.classification}_{spec}', vars=func_call_vars)
		elif spec == 'cast_bin_to_bin':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_str_to_bin':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'cast_bin_to_str':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'var_type': var_type})
		elif spec == 'list_pop':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': DSN.shift(calls, -1), 'var_type': var_type})
		elif spec == 'dict_pop':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': DSN.shift(calls, -1), 'var_type': var_type})
		elif spec == 'dict_keys':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': DSN.shift(calls, -1), 'var_type': var_type})
		elif spec == 'dict_values':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_{spec}', vars={**func_call_vars, 'receiver': DSN.shift(calls, -1), 'var_type': var_type})
		elif spec == 'new_enum':
			var_type = self.to_symbol_path(cast(SymbolRaw, context))
			return self.view.render(f'{node.classification}_cast_bin_to_bin', vars={**func_call_vars, 'var_type': var_type})
		else:
			return self.view.render(node.classification, vars=func_call_vars)

	def accepted_arguments(self, node: defs.FuncCall, arguments: list[str]) -> list[str]:
		calls_raw = self.symbols.type_of(node.calls)
		node_arguments = node.arguments
		return [self.process_argument(calls_raw, index, node_arguments[index], argument) for index, argument in enumerate(arguments)]

	def process_argument(self, org_calls: SymbolRaw, arg_index: int, arg_node: defs.Argument, arg_value_str: str) -> str:
		def resolve_calls(org_calls: SymbolRaw) -> SymbolRaw:
			if isinstance(org_calls.types, defs.Class):
				return self.symbols.type_of_constructor(org_calls.types)

			return org_calls

		def actualize_parameter(calls: SymbolRaw, arg_value: SymbolRaw) -> SymbolRaw:
			calls_ref = reflection.Builder(calls) \
				.case(reflection.Method).schema(lambda: {'klass': calls.attrs[0], 'parameters': calls.attrs[1:-1], 'returns': calls.attrs[-1]}) \
				.other_case().schema(lambda: {'parameters': calls.attrs[:-1], 'returns': calls.attrs[-1]}) \
				.build(reflection.Function)
			if isinstance(calls_ref, reflection.Constructor):
				return calls_ref.parameter(arg_index, org_calls, arg_value)
			elif isinstance(calls_ref, reflection.Method):
				return calls_ref.parameter(arg_index, calls_ref.symbol.context, arg_value)
			else:
				return calls_ref.parameter(arg_index, arg_value)

		arg_value = self.symbols.type_of(arg_node.value)
		parameter = actualize_parameter(resolve_calls(org_calls), arg_value)
		return self.accepted_cvar_value(parameter, arg_node.value, arg_value, arg_value_str)

	def analyze_func_call_spec(self, node: defs.FuncCall, calls: str) -> tuple[str, SymbolRaw | None]:
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
		elif isinstance(node.calls, defs.Variable) and node.calls.tokens == 'list':
			return 'new_list', None
		elif isinstance(node.calls, defs.Variable) and node.calls.tokens in ['int', 'float', 'bool', 'str']:
			org_calls = node.calls.tokens
			casted_types = {'int': int, 'float': float, 'bool': bool, 'str': str}
			from_raw = self.symbols.type_of(node.arguments[0])
			to_type = casted_types[org_calls]
			to_raw = self.symbols.type_of_primitive(to_type)
			if self.symbols.is_a(from_raw, str):
				return 'cast_str_to_bin', to_raw
			elif to_type == str:
				return 'cast_bin_to_str', from_raw
			else:
				return 'cast_bin_to_bin', to_raw
		elif isinstance(node.calls, defs.Relay) and node.calls.prop.tokens in ['pop', 'keys', 'values']:
			prop = node.calls.prop.tokens
			context = self.symbols.type_of(node.calls).context
			if self.symbols.is_a(context, list) and prop == 'pop':
				return 'list_pop', context.attrs[0]
			elif self.symbols.is_a(context, dict) and prop in ['pop', 'keys', 'values']:
				key_attr, value_attr = context.attrs
				attr_indexs = {'pop': value_attr, 'keys': key_attr, 'values': value_attr}
				return f'dict_{prop}', attr_indexs[prop]
		elif isinstance(node.calls, (defs.Relay, defs.Variable)):
			raw = self.symbols.type_of(node.calls)
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
		calculable_value = self.calculable_cvar_value(self.symbols.type_of(node.value), value)
		return self.view.render('unary_operator', vars={'operator': operator, 'value': calculable_value})

	def on_not_compare(self, node: defs.NotCompare, operator: str, value: str) -> str:
		calculable_value = self.calculable_cvar_value(self.symbols.type_of(node.value), value)
		return self.view.render('unary_operator', vars={'operator': '!', 'value': calculable_value})

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
		left_raw = self.symbols.type_of(node_of_elements[0])
		left = self.calculable_cvar_value(left_raw, elements[0])
		for index in range(int((len(elements) - 1) / 2)):
			operator = elements[index * 2 + 1]
			right_raw = self.symbols.type_of(node_of_elements[index * 2 + 2])
			right = self.calculable_cvar_value(right_raw, elements[index * 2 + 2])
			left = self.view.render('binary_operator', vars={'left': left, 'operator': operator, 'right': right, 'right_is_dict': self.symbols.is_a(right_raw, dict)})

		return left

	def on_tenary_operator(self, node: defs.TenaryOperator, primary: str, condition: str, secondary: str) -> str:
		return self.view.render(node.classification, vars={'primary': primary, 'condition': condition, 'secondary': secondary})

	# Literal

	def on_string(self, node: defs.String) -> str:
		return node.tokens.replace("'", '"')

	def on_comment(self, node: defs.Comment) -> str:
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
