from enum import Enum
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
import rogw.tranp.node.definition as defs
from rogw.tranp.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.view.render import Renderer


class Py2Cpp(Procedure[str]):
	def __init__(self, symbols: Symbols, render: Renderer, options: TranslatorOptions) -> None:
		super().__init__(verbose=options.verbose)
		self.symbols = symbols
		self.view = render

	def accepted_cvar_value(self, accept_raw: SymbolRaw, value_node: Node, value_raw: SymbolRaw, value_str: str, declared: bool = False) -> str:
		value_on_new = isinstance(value_node, defs.FuncCall) and self.symbols.type_of(value_node.calls).types.is_a(defs.Class)
		move = CVars.analyze_move(accept_raw, value_raw, value_on_new, declared)
		if move == CVars.Moves.Deny:
			raise LogicError(f'Unacceptable value move. accept: {str(accept_raw)}, value: {str(value_raw)}, value_on_new: {value_on_new}, declared: {declared}')

		if move == CVars.Moves.MakeSp:
			# XXX 関数名(クラス名)と引数を分離。必ず取得できるので警告を抑制(期待値: `Class(a, b, c)`)
			matches = cast(re.Match, re.fullmatch(r'([^(]+)\((.*)\)', value_str))
			return self.view.render('cvar_move', vars={'move': move.name, 'var_type': matches[1], 'arguments': matches[2]})
		else:
			return self.view.render('cvar_move', vars={'move': move.name, 'value': value_str})

	# Hook

	def on_exit_func_call(self, node: defs.FuncCall, result: str) -> str:
		if result.startswith('directive'):
			return node.arguments[0].tokens[1:-1]
		else:
			return result

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

	def on_for(self, node: defs.For, symbol: str, for_in: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'iterates': for_in, 'statements': statements})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements, 'catches': catches})

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'comment': comment, 'statements': statements}
		return self.view.render(node.classification, vars=function_vars)

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'comment': comment, 'statements': statements, }
		method_vars = {'access': node.access, 'class_symbol': node.class_types.symbol.tokens}
		return self.view.render(node.classification, vars={**function_vars, **method_vars})

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, comment: str, statements: list[str]) -> str:
		this_vars = node.this_vars

		# クラスの初期化ステートメントとそれ以外を分離
		normal_statements: list[str] = []
		initializer_statements: list[str] = []
		super_initializer_statement = ''
		for index, statement in enumerate(node.statements):
			if statement in this_vars:
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
		for index, var in enumerate(this_vars):
			# XXX 代入式の右辺を取得。必ず取得できるのでキャストして警告を抑制 (期待値: `int this->a = 1234;`)
			initialize_value = cast(re.Match[str], re.search(r'=\s*([^;]+);$', initializer_statements[index]))[1]
			for in_symbol in var.symbols:
				decl_var_symbol = in_symbol.as_a(defs.DeclThisVar)
				initializers.append({'symbol': decl_var_symbol.tokens_without_this, 'value': initialize_value})

		class_name = node.class_types.alias_symbol or node.class_types.symbol.tokens
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'comment': comment, 'statements': normal_statements}
		method_vars = {'access': node.access, 'class_symbol': class_name}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(node.classification, vars={**function_vars, **method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'comment': comment, 'statements': statements}
		method_vars = {'access': node.access, 'class_symbol': node.class_types.symbol.tokens}
		return self.view.render(node.classification, vars={**function_vars, **method_vars})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, comment: str, statements: list[str]) -> str:
		function_vars = {'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': statements}
		closure_vars = {'binded_this': node.binded_this}
		return self.view.render(node.classification, vars={**function_vars, **closure_vars})

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], inherits: list[str], comment: str, statements: list[str]) -> str:
		# XXX メンバー変数の展開方法を検討
		vars: list[str] = []
		for class_var in node.class_vars:
			for in_symbol in class_var.symbols:
				decl_var_symbol = in_symbol.as_a(defs.DeclClassVar)
				var_type = self.symbols.type_of(class_var.var_type).make_shorthand(use_alias=True)
				class_var_vars = {'is_static': True, 'access': defs.to_access(decl_var_symbol.tokens), 'symbol': decl_var_symbol.tokens, 'var_type': var_type}
				vars.append(self.view.render('class_decl_var', vars=class_var_vars))

		for this_var in node.this_vars:
			for in_symbol in this_var.symbols:
				decl_var_symbol = in_symbol.as_a(defs.DeclThisVar)
				var_type = self.symbols.type_of(this_var.var_type).make_shorthand(use_alias=True)
				this_var_vars = {'is_static': False, 'access': defs.to_access(decl_var_symbol.tokens_without_this), 'symbol': decl_var_symbol.tokens_without_this, 'var_type': var_type}
				vars.append(self.view.render('class_decl_var', vars=this_var_vars))

		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'inherits': inherits, 'comment': comment, 'statements': statements, 'vars': vars})

	def on_enum(self, node: defs.Enum, symbol: str, decorators: list[str], inherits: list[str], comment: str, statements: list[str]) -> str:
		add_vars = {}
		if not node.parent.is_a(defs.Entrypoint):
			add_vars = {'access': node.access}

		return self.view.render(node.classification, vars={'symbol': symbol, 'comment': comment, 'statements': statements, **add_vars})

	def on_alt_class(self, node: defs.AltClass, symbol: str, actual_class: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'actual_class': actual_class})

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})

	def on_decorator(self, node: defs.Decorator, path: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'path': path, 'arguments': arguments})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		receiver_raw = self.symbols.type_of(node.receiver)
		value_raw = self.symbols.type_of(node.value)

		# 変数宣言を伴う場合は変数の型を取得
		declared = receiver_raw.decl == node
		var_type = ''
		if declared:
			# フルパスの接頭辞をスコープから取得
			remain_scope = value_raw.types.scope.replace(f'{value_raw.types.module_path}.', '')
			remain_elems = DSN.elements(remain_scope)[:-1]
			fullyname = node.module_path
			for elem in remain_elems:
				in_symbol = self.symbols.from_fullyname(DSN.join(fullyname, elem))
				fullyname = DSN.join(fullyname, in_symbol.types.alias_symbol or in_symbol.types.domain_name)

			# いずれのスコープ上でも参照出来るようにフルパスで指定(例: `Class` -> `A::B::Class`)
			prefix = DSN.join(*DSN.elements(DSN.shift(fullyname, 1)), delimiter='::')
			var_type = DSN.join(prefix, value_raw.make_shorthand(use_alias=True), delimiter='::')

		accepted_value = self.accepted_cvar_value(receiver_raw, node.value, self.symbols.type_of(node.value), value, declared=declared)
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': accepted_value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		accepted_value = self.accepted_cvar_value(self.symbols.type_of(node.receiver), node.value, self.symbols.type_of(node.value), value, declared=True)
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': accepted_value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, operator: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'operator': operator, 'value': value})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		function = node.parent.as_a(defs.Block).parent.as_a(defs.Function)
		accepted_value = self.accepted_cvar_value(self.symbols.type_of(function).attrs[-1], node.return_value, self.symbols.type_of(node.return_value), return_value)
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
		return node.class_types.as_a(defs.ClassDef).alias_symbol or node.tokens

	def on_import_name(self, node: defs.ImportName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		receiver_symbol = self.symbols.type_of(node.receiver)
		prop_symbol = self.symbols.type_of_property(receiver_symbol.types, node.prop)
		prop = prop_symbol.types.alias_symbol or node.prop.tokens

		def is_cvar_receiver() -> bool:
			return len(receiver_symbol.attrs) > 0 and receiver_symbol.attrs[0].types.symbol.tokens in CVars.keys()

		def is_this_var() -> bool:
			return node.receiver.is_a(defs.ThisRef)

		def is_static_access() -> bool:
			is_class_alias = isinstance(node.receiver, (defs.ClassRef, defs.Super))
			is_class_direct = receiver_symbol.types.fullyname.endswith(node.receiver.tokens)
			return is_class_alias or is_class_direct

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
		return symbol.types.alias_symbol or node.tokens

	def on_indexer(self, node: defs.Indexer, receiver: str, key: str) -> str:
		if key in CVars.keys():
			# XXX 互換用の型は不要なので除外
			return receiver
		else:
			return f'{receiver}[{key}]'

	def on_type_relay(self, node: defs.TypeRelay, receiver: str) -> str:
		receiver_symbol = self.symbols.type_of(node.receiver)
		prop_symbol = self.symbols.type_of_property(receiver_symbol.types, node.prop)
		type_name = prop_symbol.types.alias_symbol or node.prop.tokens
		return self.view.render(node.classification, vars={'receiver': receiver, 'type_name': type_name})

	def on_type_var(self, node: defs.TypeVar) -> str:
		symbol = self.symbols.type_of(node)
		type_name = symbol.types.alias_symbol or node.type_name.tokens
		return self.view.render(node.classification, vars={'type_name': type_name})

	def on_list_type(self, node: defs.ListType, type_name: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, type_name: str, key_type: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'key_type': key_type, 'value_type': value_type})

	def on_callable_type(self, node: defs.CallableType, type_name: str, parameters: list[str], return_type: str) -> str:
		raise NotImplementedError(f'Not supported CallableType. symbol: {node.fullyname}')

	def on_custom_type(self, node: defs.CustomType, type_name: str, template_types: list[str]) -> str:
		return self.view.render(node.classification, vars={'type_name': type_name, 'cvar_type': template_types[0], 'cmutable': template_types[1] if len(template_types) == 2 else ''})

	def on_union_type(self, node: defs.UnionType, type_name: str, or_types: list[str]) -> str:
		raise NotImplementedError(f'Not supported UnionType. symbol: {node.fullyname}')

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		def process_argument(org_calls: SymbolRaw, arg_index: int, arg_node: defs.Argument, arg_value_str: str) -> str:
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

		# 実引数を受け入れ可能な形式に変換
		calls_raw = self.symbols.type_of(node.calls)
		node_arguments = node.arguments
		accepted_arguments = [process_argument(calls_raw, index, node_arguments[index], argument) for index, argument in enumerate(arguments)]

		# Block直下の場合はステートメント
		is_statement = node.parent.is_a(defs.Block)
		return self.view.render(node.classification, vars={'calls': calls, 'arguments': accepted_arguments, 'is_statement': is_statement})


	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		return node.super_class_symbol.tokens

	def on_argument(self, node: defs.Argument, label: str, value: str) -> str:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: str) -> str:
		return class_type

	# Operator

	def on_factor(self, node: defs.Factor, operator: str, value: str) -> str:
		return f'{operator}{value}'

	def on_not_compare(self, node: defs.NotCompare, operator: str, value: str) -> str:
		return f'!{value}'

	def on_or_compare(self, node: defs.OrCompare, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, '||', right)

	def on_and_compare(self, node: defs.AndCompare, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, '&&', right)

	def on_comparison(self, node: defs.Comparison, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_or_bitwise(self, node: defs.OrBitwise, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_xor_bitwise(self, node: defs.XorBitwise, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_and_bitwise(self, node: defs.AndBitwise, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_sum(self, node: defs.Sum, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_term(self, node: defs.Term, left: str, operator: str, right: list[str]) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_binary_operator(self, node: defs.BinaryOperator, left: str, operator: str, right: list[str]) -> str:
		joined_right = f' {operator} '.join(right)
		return f'{left} {operator} {joined_right}'

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


class CVars:
	class Moves(Enum):
		Copy = 0
		New = 1
		MakeSp = 2
		ToActual = 3
		ToAddress = 4
		UnpackSp = 5
		Deny = 6

	@classmethod
	def analyze_move(cls, accept: SymbolRaw, value: SymbolRaw, value_on_new: bool, declared: bool) -> Moves:
		accept_key = cls.key_from(accept)
		value_key = cls.key_from(value)
		if cls.is_raw_ref(accept_key) and not declared:
			return cls.Moves.Deny

		if cls.is_addr_sp(accept_key) and cls.is_raw(value_key) and value_on_new:
			return cls.Moves.MakeSp
		elif cls.is_addr_p(accept_key) and cls.is_raw(value_key) and value_on_new:
			return cls.Moves.New
		elif cls.is_addr_p(accept_key) and cls.is_raw(value_key):
			return cls.Moves.ToAddress
		elif cls.is_raw(accept_key) and cls.is_addr(value_key):
			return cls.Moves.ToActual
		elif cls.is_addr_p(accept_key) and cls.is_addr_sp(value_key):
			return cls.Moves.UnpackSp
		elif cls.is_addr_p(accept_key) and cls.is_addr_p(value_key):
			return cls.Moves.Copy
		elif cls.is_addr_sp(accept_key) and cls.is_addr_sp(value_key):
			return cls.Moves.Copy
		elif cls.is_raw(accept_key) and cls.is_raw(value_key):
			return cls.Moves.Copy
		else:
			return cls.Moves.Deny

	@classmethod
	def is_raw(cls, key: str) -> bool:
		return key in [cpp.CRaw.__name__, cpp.CRef.__name__]

	@classmethod
	def is_addr(cls, key: str) -> bool:
		return key in [cpp.CP.__name__, cpp.CSP.__name__]

	@classmethod
	def is_raw_ref(cls, key: str) -> bool:
		return key == cpp.CRef.__name__

	@classmethod
	def is_addr_p(cls, key: str) -> bool:
		return key == cpp.CP.__name__

	@classmethod
	def is_addr_sp(cls, key: str) -> bool:
		return key == cpp.CSP.__name__

	@classmethod
	def keys(cls) -> list[str]:
		return [cvar.__name__ for cvar in [cpp.CP, cpp.CSP, cpp.CRef, cpp.CRaw]]

	@classmethod
	def key_from(cls, raw: SymbolRaw) -> str:
		keys = [attr.types.symbol.tokens for attr in raw.attrs]
		if len(keys) > 0 and keys[0] in cls.keys():
			return keys[0]

		return cpp.CRaw.__name__
