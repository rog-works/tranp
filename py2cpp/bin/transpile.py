import os
import sys

from py2cpp.analize.procedure import Procedure
from py2cpp.analize.symbols import Symbols
from py2cpp.app.app import App
from py2cpp.ast.parser import ParserSetting
from py2cpp.lang.error import stacktrace
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.view.render import Renderer, Writer


class Handler(Procedure[str]):
	def __init__(self, symbols: Symbols, render: Renderer) -> None:
		super().__init__()
		self.symbols = symbols
		self.view = render

	def __result_internal(self, begin: Node) -> str:
		cloning = Handler(self.symbols, self.view)
		for node in begin.calculated():
			cloning.process(node)

		cloning.process(begin)
		return cloning.result()

	# Hook

	def on_exit_func_call(self, node: defs.FuncCall, result: str) -> str:
		if result == "pragma('once')":
			return '#pragma once'
		else:
			return result

	# General

	def on_entrypoint(self, node: defs.Entrypoint, statements: list[str]) -> str:
		return self.view.render('block', vars={'statements': statements})

	# Statement - compound

	def on_if(self, node: defs.If, condition: str, block: str, else_ifs: list[str], else_block: str) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'block': block, 'else_ifs': else_ifs, 'else_block': else_block})

	def on_else_if(self, node: defs.ElseIf, condition: str, block: str) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'block': block})

	def on_while(self, node: defs.While, condition: str, block: str) -> str:
		return self.view.render(node.classification, vars={'condition': condition, 'block': block})

	def on_for(self, node: defs.For, symbol: str, iterates: str, block: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'iterates': iterates, 'block': block})

	def on_try(self, node: defs.Try, block: str, catches: list[str]) -> str:
		return self.view.render(node.classification, vars={'block': block, 'catches': catches})

	def on_catch(self, node: defs.Catch, symbol: str, alias: str, block: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'alias': alias, 'block': block})

	def on_function(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'block': block})

	def on_class_method(self, node: defs.ClassMethod, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str) -> str:
		return self.on_method_type(node, symbol, decorators, parameters, return_decl, block, node.class_symbol.tokens)

	def on_constructor(self, node: defs.Constructor, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str) -> str:
		add_vars = {'initializer': [], 'class_symbol': node.class_symbol.tokens}
		for var in node.this_vars:
			var_symbol = var.symbol.as_a(defs.ThisVar)
			add_vars['initializer'].append({'symbol': var_symbol.tokens_without_this, 'value': var.value.tokens})

		return self.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'block': block, **add_vars})

	def on_method(self, node: defs.Method, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str) -> str:
		return self.on_method_type(node, symbol, decorators, parameters, return_decl, block, node.class_symbol.tokens)

	def on_method_type(self, node: defs.Function, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str, class_symbol: str) -> str:
		return self.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'block': block, 'class_symbol': class_symbol})

	def on_closure(self, node: defs.Closure, symbol: str, decorators: list[str], parameters: list[str], return_decl: str, block: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_decl, 'block': block, 'binded_this': node.binded_this})

	def on_class(self, node: defs.Class, symbol: str, decorators: list[str], parents: list[str], block: str) -> str:
		# FIXME メンバー変数の展開方法を再検討
		vars: list[dict[str, str]] = []
		for var in node.vars:
			if var.is_a(defs.MoveAssign):
				vars.append({'access': 'public', 'symbol': var.symbol.tokens, 'var_type': 'Unknown', 'value': var.value.tokens})
			else:
				vars.append({'access': 'public', 'symbol': var.symbol.tokens, 'var_type': var.as_a(defs.AnnoAssign).var_type.tokens, 'value': var.value.tokens})

		return self.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parents': parents, 'block': block, 'vars': vars})

	def on_enum(self, node: defs.Enum, symbol: str, block: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'block': block})

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, symbol: str, var_type: str, default_value: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})

	def on_return_decl(self, node: defs.ReturnDecl, var_type: str) -> str:
		return var_type if not node.var_type.is_a(defs.Null) else 'void'

	def on_decorator(self, node: defs.Decorator, symbol: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'arguments': arguments})

	def on_block(self, node: defs.Block, statements: list[str]) -> str:
		return self.view.render(node.classification, vars={'statements': statements})

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, receiver: str, value: str) -> str:
		declared = len([decl_var for decl_var in node.parent.as_a(defs.Block).decl_vars_with(defs.MoveAssign) if decl_var == node]) > 0
		var_type = ''
		if declared:
			value_type = self.symbols.type_of(node.value)
			var_type = self.__result_internal(value_type.types)

		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_anno_assign(self, node: defs.AnnoAssign, receiver: str, var_type: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'var_type': var_type, 'value': value})

	def on_aug_assign(self, node: defs.AugAssign, receiver: str, operator: str, value: str) -> str:
		return self.view.render(node.classification, vars={'receiver': receiver, 'operator': operator, 'value': value})

	def on_return(self, node: defs.Return, return_value: str) -> str:
		return self.view.render(node.classification, vars={'return_value': return_value})

	def on_throw(self, node: defs.Throw, calls: str, via: str) -> str:
		return self.view.render(node.classification, vars={'calls': calls, 'via': via})

	def on_pass(self, node: defs.Pass) -> None:
		pass

	def on_break(self, node: defs.Break) -> str:
		return 'break;'

	def on_continue(self, node: defs.Continue) -> str:
		return 'continue;'

	def on_import(self, node: defs.Import) -> str:
		module_path = node.module_path.tokens
		text = self.view.render(node.classification, vars={'module_path': module_path})
		return text if module_path.startswith('FW') else f'// {text}'

	# Primary

	def on_class_var(self, node: defs.ClassVar) -> str:
		return node.tokens

	def on_this_var(self, node: defs.ThisVar) -> str:
		return node.tokens.replace('self', 'this')

	def on_param_class(self, node: defs.ParamClass) -> str:
		return node.tokens

	def on_param_this(self, node: defs.ParamThis) -> str:
		return node.tokens

	def on_local_var(self, node: defs.LocalVar) -> str:
		return node.tokens

	def on_types_name(self, node: defs.TypesName) -> str:
		return node.tokens

	def on_import_name(self, node: defs.ImportName) -> str:
		return node.tokens

	def on_relay(self, node: defs.Relay, receiver: str) -> str:
		# FIXME receiverの形態によってアクセス演算子を変える必要がある
		return f'{receiver}.{node.prop.tokens}'

	def on_var(self, node: defs.Var) -> str:
		return node.tokens

	def on_indexer(self, node: defs.Indexer, symbol: str, key: str) -> str:
		return f'{symbol}[{key}]'

	def on_general_type(self, node: defs.GeneralType) -> str:
		return node.symbol.tokens

	def on_list_type(self, node: defs.ListType, symbol: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'value_type': value_type})

	def on_dict_type(self, node: defs.DictType, symbol: str, key_type: str, value_type: str) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'key_type': key_type, 'value_type': value_type})

	def on_custom_type(self, node: defs.CustomType, symbol: str, template_types: list[str]) -> str:
		return self.view.render(node.classification, vars={'symbol': symbol, 'template_types': template_types})

	def on_union_type(self, node: defs.UnionType, symbol: str, or_types: list[str]) -> str:
		raise NotImplementedError(f'Not supported UnionType. via: {node}')

	def on_null_type(self, node: defs.NullType) -> str:
		return 'void'

	def on_func_call(self, node: defs.FuncCall, calls: str, arguments: list[str]) -> str:
		return self.view.render(node.classification, vars={'calls': calls, 'arguments': arguments})

	def on_super(self, node: defs.Super, calls: str, arguments: list[str]) -> str:
		return self.view.render('func_call', vars={'calls': node.parent_symbol.tokens, 'arguments': arguments})

	# Common

	def on_argument(self, node: defs.Argument, value: str) -> str:
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

	def on_pair(self, node: defs.Pair, first: str, second: str) -> str:
		return '{' f'{first}, {second}' '}'

	def on_list(self, node: defs.List, values: list[str]) -> str:
		return self.view.render(node.classification, vars={'values': values})

	def on_dict(self, node: defs.Dict, items: list[str]) -> str:
		return self.view.render(node.classification, vars={'items': items})

	def on_truthy(self, node: defs.Truthy) -> str:
		return 'true'

	def on_falsy(self, node: defs.Falsy) -> str:
		return 'false'

	def on_null(self, node: defs.Null) -> str:
		return 'nullptr'

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
			print('action:', str(node))
			handler.process(node)

		writer.put(handler.result())
		writer.flush()
	except Exception as e:
		print(''.join(stacktrace(e)))


if __name__ == '__main__':
	definitions = {
		f'{Args.__module__}.{Args.__name__}': Args,
		f'{Writer.__module__}.{Writer.__name__}': make_writer,
		f'{Renderer.__module__}.{Renderer.__name__}': make_renderer,
		f'{Handler.__module__}.{Handler.__name__}': Handler,
		'py2cpp.ast.parser.ParserSetting': make_parser_setting,
		'py2cpp.module.types.ModulePath': make_module_path,
	}
	App(definitions).run(task)
