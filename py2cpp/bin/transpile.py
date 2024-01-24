import os
import re
import sys
from typing import cast

from py2cpp.analize.procedure import Procedure
from py2cpp.analize.symbols import Symbol, Symbols
from py2cpp.app.app import App
from py2cpp.ast.parser import ParserSetting
import py2cpp.compatible.cpp.object as cpp
import py2cpp.compatible.python.embed as __alias__
from py2cpp.lang.error import stacktrace
from py2cpp.lang.module import fullyname
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.view.render import Renderer, Writer


class Handler(Procedure[str]):
	def __init__(self, symbols: Symbols, render: Renderer) -> None:
		super().__init__(verbose=True)
		self.symbols = symbols
		self.view = render

	# XXX 未使用
	# def __result_internal(self, begin: Node) -> str:
	# 	cloning = Handler(self.symbols, self.view)
	# 	for node in begin.calculated():
	# 		cloning.process(node)

	# 	cloning.process(begin)
	# 	return cloning.result()

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

	def on_for(self, node: defs.For, symbol: str, iterates: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'iterates': iterates, 'statements': statements})

	def on_catch(self, node: defs.Catch, var_type: str, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'var_type': var_type, 'symbol': symbol, 'statements': statements})

	def on_try(self, node: defs.Try, statements: list[str], catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements, 'catches': catches})

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': statements})

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': statements, 'class_symbol': node.class_symbol.tokens})

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, statements: list[str]) -> str:
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
			# XXX 代入式の右辺を取得。必ず取得できるのでキャストして警告を抑制 (期待値: `int this.a = 1234;`)
			initialize_value = cast(re.Match[str], re.search(r'=\s*([^;]+);$', initializer_statements[index]))[1]
			decl_var_symbol = var.symbol.as_a(defs.DeclThisVar)
			initializers.append({'symbol': decl_var_symbol.tokens_without_this, 'value': initialize_value})

		method_vars = {'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': normal_statements, 'class_symbol': node.class_symbol.tokens}
		constructor_vars = {'initializers': initializers, 'super_initializer': super_initializer}
		return self.view.render(node.classification, vars={**method_vars, **constructor_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': statements, 'class_symbol': node.class_symbol.tokens})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'statements': statements, 'binded_this': node.binded_this})

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], parents: list[str], statements: list[str]) -> str:
		# XXX メンバー変数の展開方法を検討
		vars: list[str] = []
		for class_var in node.class_vars:
			decl_var_symbol = class_var.symbol.as_a(defs.DeclClassVar)
			vars.append(self.view.render('class_decl_var', vars={'is_static': True, 'access': 'public', 'symbol': decl_var_symbol.tokens, 'var_type': class_var.var_type.tokens}))

		for this_var in node.this_vars:
			decl_var_symbol = this_var.symbol.as_a(defs.DeclThisVar)
			vars.append(self.view.render('class_decl_var', vars={'is_static': False, 'access': 'public', 'symbol': decl_var_symbol.tokens_without_this, 'var_type': this_var.var_type.tokens}))

		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parents': parents, 'statements': statements, 'vars': vars})

	def on_enum(self, node: defs.Enum, symbol: str, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'statements': statements})

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})

	def on_decorator(self, node: defs.Decorator, path: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'path': path, 'arguments': arguments})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		# XXX ローカル変数の宣言を伴うステートメントか判定
		decl_vars = [decl_var for decl_var in node.parent.as_a(defs.Block).decl_vars_with(defs.DeclLocalVar)]
		declared = len([decl_var for decl_var in decl_vars if decl_var == node]) > 0

		# XXX 変数の型名を取得
		var_type = ''
		if declared:
			value_type = self.symbols.type_of(node.value)
			var_type = self.view.render('move_assign_var_type', vars={'var_type': str(value_type)})

		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, operator: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'operator': operator, 'value': value})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		def analyze_cvar_return_symbol() -> Symbol | None:
			function = node.function.as_a(defs.Function)
			if not isinstance(node.return_value, defs.FuncCall):
				return None

			is_cvar_return = function.return_type.is_a(defs.CustomType)
			if not is_cvar_return:
				return None

			calls_symbol = self.symbols.type_of(node.return_value.calls)
			is_call_constructor = calls_symbol.raw.decl.is_a(defs.Class)
			if not is_call_constructor:
				return None

			return self.symbols.type_of(function.return_type)

		cvar_return_symbol = analyze_cvar_return_symbol()
		if cvar_return_symbol is not None:
			cvar_type = cvar_return_symbol.attrs[0].types.symbol.tokens
			return self.view.render(node.classification, vars={'return_value': return_value, 'cvar_type': cvar_type})
		else:
			return self.view.render(node.classification, vars={'return_value': return_value, 'cvar_type': ''})

	def on_throw(self, node: defs.Throw, throws: str, via: str) -> str:
		return self.view.render(node.classification, vars={'throws': throws, 'via': via})

	def on_pass(self, node: defs.Pass) -> None:
		pass

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_import(self, node: defs.Import) -> str:
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
		return node.class_types.as_a(defs.ClassKind).alias_symbol() or node.tokens

	def on_import_name(self, node: defs.ImportName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		def is_static_access(receiver_symbol: Symbol) -> bool:
			if isinstance(receiver_symbol.types, defs.Enum):
				return True
			elif isinstance(node.receiver, defs.ClassRef):
				return True
			elif isinstance(node.receiver, defs.Super):
				return True

			prop_symbol = self.symbols.type_of_property(receiver_symbol.types, node.prop)
			prop_symbol_decl = prop_symbol.raw.decl
			if isinstance(prop_symbol.types, (defs.Enum, defs.ClassMethod)):
				return True
			elif isinstance(prop_symbol_decl, defs.AnnoAssign) and prop_symbol_decl.symbol.is_a(defs.DeclClassVar):
				return True

			return False

		cvars: list[str] = [cvar.__name__ for cvar in [cpp.CP, cpp.CSP, cpp.CRef, cpp.CRaw]]
		receiver_symbol = self.symbols.type_of(node.receiver)
		is_cvar_receiver = len(receiver_symbol.attrs) > 0 and receiver_symbol.attrs[0].types.symbol.tokens in cvars
		if is_cvar_receiver:
			cvar_type = receiver_symbol.attrs[0].types.symbol.tokens
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': cvar_type, 'prop': node.prop.tokens})
		elif node.receiver.is_a(defs.ThisRef):
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'arrow', 'prop': node.prop.tokens})
		elif is_static_access(receiver_symbol):
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'static', 'prop': node.prop.tokens})
		else:
			return self.view.render(node.classification, vars={'receiver': receiver, 'accessor': 'dot', 'prop': node.prop.tokens})

	def on_class_ref(self, node: defs.ClassRef) -> str:
		return node.class_symbol.tokens

	def on_this_ref(self, node: defs.ThisRef) -> str:
		return 'this'

	def on_argument_label(self, node: defs.ArgumentLabel) -> str:
		return node.tokens

	def on_variable(self, node: defs.Variable) -> str:
		return node.tokens

	def on_indexer(self, node: defs.Indexer, receiver: str, key: str) -> str:
		return f'{receiver}[{key}]'

	def on_general_type(self, node: defs.GeneralType) -> str:
		return node.type_name.tokens

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
		# Block直下の場合はステートメント
		is_statement = node.parent.is_a(defs.Block)
		return self.view.render(node.classification, vars={'calls': calls, 'arguments': arguments, 'is_statement': is_statement})

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		return node.parent_class_symbol.tokens

	def on_argument(self, node: defs.Argument, label: str, value: str) -> str:
		return value

	def on_inherit_argument(self, node: defs.InheritArgument, class_type: str) -> str:
		return class_type

	# Operator

	def on_factor(self, node: defs.Factor, operator: str, value: str) -> str:
		return f'{operator}{value}'

	def on_not_compare(self, node: defs.NotCompare, operator: str, value: str) -> str:
		return f'!{value}'

	def on_or_compare(self, node: defs.OrCompare, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_and_compare(self, node: defs.AndCompare, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_comparison(self, node: defs.Comparison, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_or_bitwise(self, node: defs.OrBitwise, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_xor_bitwise(self, node: defs.XorBitwise, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_and_bitwise(self, node: defs.AndBitwise, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_sum(self, node: defs.Sum, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_term(self, node: defs.Term, left: str, operator: str, right: str) -> str:
		return self.on_binary_operator(node, left, operator, right)

	def on_binary_operator(self, node: defs.BinaryOperator, left: str, operator: str, right: str) -> str:
		return f'{left} {operator} {right}'

	# Literal

	def on_string(self, node: defs.String) -> str:
		return node.tokens.replace("'", '"')

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


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.source = args['source']
		self.template_dir = args['template_dir']

	def __parse_argv(self, argv: list[str]) -> dict[str, str]:
		args = {
			'grammar': '',
			'source': '',
			'template_dir': '', 
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-s':
				args['source'] = argv.pop(0)
			elif arg == '-t':
				args['template_dir'] = argv.pop(0)

		return args


def make_writer(args: Args) -> Writer:
	basepath, _ = os.path.splitext(args.source)
	output = f'{basepath}.cpp'
	return Writer(output)


def make_renderer(args: Args) -> Renderer:
	return Renderer(args.template_dir)


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_path(args: Args) -> ModulePath:
	basepath, _ = os.path.splitext(args.source)
	module_path = basepath.replace('/', '.')
	return ModulePath('__main__', module_path)


def task(handler: Handler, root: Node, writer: Writer) -> None:
	try:
		flatted = root.calculated()
		flatted.append(root)  # XXX

		for node in flatted:
			handler.process(node)

		writer.put(handler.result())
		writer.flush()
	except Exception as e:
		print(''.join(stacktrace(e)))


if __name__ == '__main__':
	definitions = {
		fullyname(Args): Args,
		fullyname(Writer): make_writer,
		fullyname(Renderer): make_renderer,
		fullyname(Handler): Handler,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(ModulePath): make_module_path,
	}
	App(definitions).run(task)
