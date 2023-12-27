from typing import Generic, Iterator, TypedDict, TypeVar

from py2cpp.errors import LogicError
from py2cpp.lang.error import stacktrace
from py2cpp.lang.eventemitter import EventEmitter, T_Callback
import py2cpp.node.definition as defs
from py2cpp.node.definitions import make_settings
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.serializer import serialize
from py2cpp.view.render import Renderer, Writer

T_Node = TypeVar('T_Node', bound=Node)
T_Result = TypeVar('T_Result')

T_VarVar = TypedDict('T_VarVar', {'access': str, 'symbol': str, 'var_type': str, 'initial_value': str})
T_ClassVar = TypedDict('T_ClassVar', {'vars': list[T_VarVar]})

T = TypeVar('T')


class Registry(Generic[T]):
	def __init__(self) -> None:
		self.__stack: list[T] = []

	def __len__(self) -> int:
		return len(self.__stack)

	def push(self, entry: T) -> None:
		self.__stack.append(entry)

	def pop(self, entry_type: type[T]) -> T:
		return self.__stack.pop()

	def each_pop(self, counts: int = -1) -> Iterator[T]:
		if counts < -1 or len(self) < counts:
			raise LogicError(counts, len(self))

		loops =  len(self) if counts == -1 else counts
		for _ in range(loops):
			yield self.__stack.pop()


class Context:
	def __init__(self, registry: Registry[tuple[Node, str]], writer: Writer, view: Renderer) -> None:
		self.__emitter = EventEmitter()
		self.registry = registry
		self.writer = writer
		self.view = view

	def emit(self, action: str, **kwargs) -> None:
		self.__emitter.emit(action, **kwargs)

	def on(self, action: str, callback: T_Callback) -> None:
		self.__emitter.on(action, callback)

	def off(self, action: str, callback: T_Callback) -> None:
		self.__emitter.off(action, callback)


class Handler:
	def on_action(self, node: Node, ctx: Context) -> None:
		self.enter(node, ctx)
		self.action(node, ctx)
		self.exit(node, ctx)

	def action(self, node: Node, ctx: Context) -> None:
		handler_name = f'on_{node.classification}'
		if hasattr(self, handler_name):
			getattr(self, handler_name)(node, ctx)
		else:
			self.on_terminal(node, ctx)

	def enter(self, node: Node, ctx: Context) -> None:
		handler_name = f'on_enter_{node.classification}'
		if hasattr(self, handler_name):
			getattr(self, handler_name)(node, ctx)

	def exit(self, node: Node, ctx: Context) -> None:
		handler_name = f'on_exit_{node.classification}'
		if hasattr(self, handler_name):
			getattr(self, handler_name)(node, ctx)

	# Hook

	def on_exit_func_call(self, node: defs.FuncCall, ctx: Context) -> None:
		_, result = ctx.registry.pop(tuple[defs.FuncCall, str])
		if result == "pragma('once')":
			ctx.registry.push((node, '#pragma once'))
		else:
			ctx.registry.push((node, result))

	# General

	def on_entrypoint(self, node: defs.Entrypoint, ctx: Context) -> None:
		statements = [statement for _, statement in ctx.registry.each_pop()]
		statements.reverse()
		text = ctx.view.render('block', vars={'statements': statements})
		ctx.writer.put(text)

	# Statement - compound

	def on_if(self, node: defs.If, ctx: Context) -> None:
		_, else_block = ctx.registry.pop(tuple[defs.Block, str])
		else_ifs = [else_if for _, else_if in ctx.registry.each_pop(len(node.else_ifs))]
		else_ifs.reverse()
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, condition = ctx.registry.pop(tuple[defs.Node, str])
		text = ctx.view.render(node.classification, vars={'condition': condition, 'block': block, 'else_ifs': else_ifs, 'else_block': else_block})
		ctx.registry.push((node, text))

	def on_else_if(self, node: defs.ElseIf, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, condition = ctx.registry.pop(tuple[defs.Node, str])
		text = ctx.view.render(node.classification, vars={'condition': condition, 'block': block})
		ctx.registry.push((node, text))

	def on_while(self, node: defs.While, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, condition = ctx.registry.pop(tuple[defs.Node, str])
		text = ctx.view.render(node.classification, vars={'condition': condition, 'block': block})
		ctx.registry.push((node, text))

	def on_for(self, node: defs.For, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, iterates = ctx.registry.pop(tuple[defs.Node, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'iterates': iterates, 'block': block})
		ctx.registry.push((node, text))

	def on_try(self, node: defs.Try, ctx: Context) -> None:
		catches = [catch for _, catch in ctx.registry.each_pop(len(node.catches))]
		catches.reverse()
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		text = ctx.view.render(node.classification, vars={'block': block, 'catches': catches})
		ctx.registry.push((node, text))

	def on_catch(self, node: defs.Catch, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, alias = ctx.registry.pop(tuple[defs.Symbol, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'alias': alias, 'block': block})
		ctx.registry.push((node, text))

	def on_class(self, node: defs.Class, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		parents = [parent for  _, parent in ctx.registry.each_pop(len(node.parents))]
		parents.reverse()
		decorators = [decorator for  _, decorator in ctx.registry.each_pop(len(node.decorators))]
		decorators.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={**serialize(node, T_ClassVar), 'symbol': symbol, 'decorators': decorators, 'parents': parents, 'block': block})
		ctx.registry.push((node, text))

	def on_enum(self, node: defs.Enum, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'block': block})
		ctx.registry.push((node, text))

	def on_function(self, node: defs.Function, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, return_type = ctx.registry.pop(tuple[defs.Block, str])
		parameters = [parameter for  _, parameter in ctx.registry.each_pop(len(node.parameters))]
		parameters.reverse()
		decorators = [decorator for  _, decorator in ctx.registry.each_pop(len(node.decorators))]
		decorators.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'block': block})
		ctx.registry.push((node, text))

	def on_constructor(self, node: defs.Constructor, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, return_type = ctx.registry.pop(tuple[defs.Block, str])
		parameters = [parameter for  _, parameter in ctx.registry.each_pop(len(node.parameters))]
		parameters.reverse()
		decorators = [decorator for  _, decorator in ctx.registry.each_pop(len(node.decorators))]
		decorators.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'block': block})
		ctx.registry.push((node, text))

	def on_class_method(self, node: defs.ClassMethod, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, return_type = ctx.registry.pop(tuple[defs.Block, str])
		parameters = [parameter for  _, parameter in ctx.registry.each_pop(len(node.parameters))]
		parameters.reverse()
		decorators = [decorator for  _, decorator in ctx.registry.each_pop(len(node.decorators))]
		decorators.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'block': block})
		ctx.registry.push((node, text))

	def on_method(self, node: defs.Method, ctx: Context) -> None:
		_, block = ctx.registry.pop(tuple[defs.Block, str])
		_, return_type = ctx.registry.pop(tuple[defs.Block, str])
		parameters = [parameter for  _, parameter in ctx.registry.each_pop(len(node.parameters))]
		parameters.reverse()
		decorators = [decorator for  _, decorator in ctx.registry.each_pop(len(node.decorators))]
		decorators.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'access': node.access, 'symbol': symbol, 'decorators': decorators, 'parameters': parameters, 'return_type': return_type, 'block': block})
		ctx.registry.push((node, text))

	# Function/Class Elements

	def on_parameter(self, node: defs.Parameter, ctx: Context) -> None:
		_, default_value = ctx.registry.pop(tuple[defs.Node, str])
		_, var_type = ctx.registry.pop(tuple[defs.Node, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'default_value': default_value})
		ctx.registry.push((node, text))

	def on_decorator(self, node: defs.Decorator, ctx: Context) -> None:
		arguments = [argument for  _, argument in ctx.registry.each_pop(len(node.arguments))]
		arguments.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'arguments': arguments})
		ctx.registry.push((node, text))

	def on_block(self, node: defs.Block, ctx: Context) -> None:
		statements = [statement for _, statement in ctx.registry.each_pop(len(node.statements))]
		statements.reverse()
		text = ctx.view.render(node.classification, vars={'statements': statements})
		ctx.registry.push((node, text))

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'value': value})
		ctx.registry.push((node, text))

	def on_anno_assign(self, node: defs.AnnoAssign, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		_, var_type = ctx.registry.pop(tuple[defs.Symbol, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'var_type': var_type, 'value': value})
		ctx.registry.push((node, text))

	def on_aug_assign(self, node: defs.AugAssign, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		_, operator = ctx.registry.pop(tuple[defs.Terminal, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'operator': operator, 'value': value})
		ctx.registry.push((node, text))

	def on_return(self, node: defs.Return, ctx: Context) -> None:
		_, return_value = ctx.registry.pop(tuple[defs.Expression, str])
		text = ctx.view.render(node.classification, vars={'return_value': return_value})
		ctx.registry.push((node, text))

	def on_throw(self, node: defs.Throw, ctx: Context) -> None:
		_, via = ctx.registry.pop(tuple[defs.Symbol, str])
		_, calls = ctx.registry.pop(tuple[defs.FuncCall, str])
		text = ctx.view.render(node.classification, vars={'calls': calls, 'via': via})
		ctx.registry.push((node, text))

	def on_pass(self, node: defs.Pass, ctx: Context) -> None:
		pass

	def on_break(self, node: defs.Break, ctx: Context) -> None:
		text = 'break;'
		ctx.registry.push((node, text))

	def on_continue(self, node: defs.Continue, ctx: Context) -> None:
		text = 'continue;'
		ctx.registry.push((node, text))

	def on_import(self, node: defs.Import, ctx: Context) -> None:
		module_path = node.module_path.tokens
		if not module_path.startswith('FW'):
			return

		text = ctx.view.render(node.classification, vars={'module_path': module_path})
		ctx.registry.push((node, text))

	# Primary

	def on_list_type(self, node: defs.ListType, ctx: Context) -> None:
		_, value_type = ctx.registry.pop(tuple[defs.Symbol, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'value_type': value_type})
		ctx.registry.push((node, text))

	def on_dict_type(self, node: defs.DictType, ctx: Context) -> None:
		_, value_type = ctx.registry.pop(tuple[defs.Symbol, str])
		_, key_type = ctx.registry.pop(tuple[defs.Symbol, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'key_type': key_type, 'value_type': value_type})
		ctx.registry.push((node, text))

	def on_union_type(self, node: defs.UnionType, ctx: Context) -> None:
		raise NotImplementedError(f'Not supported UnionType. via: {node}')

	def on_indexer(self, node: defs.Indexer, ctx: Context) -> None:
		_, key = ctx.registry.pop(tuple[defs.Expression, str])
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = f'{symbol}[{key}]'
		ctx.registry.push((node, text))

	def on_func_call(self, node: defs.FuncCall, ctx: Context) -> None:
		arguments = [argument for _, argument in ctx.registry.each_pop(len(node.arguments))]
		arguments.reverse()
		_, symbol = ctx.registry.pop(tuple[defs.Symbol, str])
		text = ctx.view.render(node.classification, vars={'symbol': symbol, 'arguments': arguments})
		ctx.registry.push((node, text))

	# Common

	def on_argument(self, node: defs.Argument, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		ctx.registry.push((node, value))

	# Operator

	def on_factor(self, node: defs.Factor, ctx: Context) -> None:
		self.on_unary_operator(node, ctx)

	def on_not_compare(self, node: defs.NotCompare, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		_, _ = ctx.registry.pop(tuple[defs.Terminal, str])
		text = f'!{value}'
		ctx.registry.push((node, text))

	def on_or_compare(self, node: defs.OrCompare, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_and_compare(self, node: defs.AndCompare, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_comparison(self, node: defs.Comparison, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_or_bitwise(self, node: defs.OrBitwise, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_xor_bitwise(self, node: defs.XorBitwise, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_and_bitwise(self, node: defs.AndBitwise, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_sum(self, node: defs.Sum, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_term(self, node: defs.Term, ctx: Context) -> None:
		self.on_binary_operator(node, ctx)

	def on_binary_operator(self, node: defs.BinaryOperator, ctx: Context) -> None:
		_, right = ctx.registry.pop(tuple[defs.Expression, str])
		_, operator = ctx.registry.pop(tuple[defs.Terminal, str])
		_, left = ctx.registry.pop(tuple[defs.Expression, str])
		text = f'{left} {operator} {right}'
		ctx.registry.push((node, text))

	def on_unary_operator(self, node: defs.UnaryOperator, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[defs.Expression, str])
		_, operator = ctx.registry.pop(tuple[defs.Terminal, str])
		text = f'{operator}{value}'
		ctx.registry.push((node, text))

	# Literal

	def on_key_value(self, node: defs.KeyValue, ctx: Context) -> None:
		_, value = ctx.registry.pop(tuple[Node, str])
		_, key = ctx.registry.pop(tuple[Node, str])
		text = '{' f'{key}, {value}' '}'
		ctx.registry.push((node, text))

	def on_dict(self, node: defs.Dict, ctx: Context) -> None:
		items = [key_value for _, key_value in ctx.registry.each_pop(len(node.items))]
		items.reverse()
		text = ctx.view.render(node.classification, vars={'items': items})
		ctx.registry.push((node, text))

	def on_list(self, node: defs.List, ctx: Context) -> None:
		values = [value for _, value in ctx.registry.each_pop(len(node.values))]
		values.reverse()
		text = ctx.view.render(node.classification, vars={'values': values})
		ctx.registry.push((node, text))

	# Expression

	def on_expression(self, node: Node, ctx: Context) -> None:  # XXX 出来れば消したい
		_, expression = ctx.registry.pop(tuple[defs.Node, str])
		ctx.registry.push((node, expression))

	# Terminal

	def on_terminal(self, node: Node, ctx: Context) -> None:
		ctx.registry.push((node, node.tokens))


class Runner:
	def __init__(self, handler: Handler) -> None:
		self.__handler = handler

	def run(self, root: Node, ctx: Context) -> None:
		try:
			ctx.on('action', self.__handler.on_action)

			flatted = root.calculated()
			flatted.append(root)  # XXX

			for node in flatted:
				print('action:', str(node))
				ctx.emit('action', node=node, ctx=ctx)

			ctx.writer.flush()

			ctx.off('action', self.__handler.on_action)
		except Exception as e:
			print(''.join(stacktrace(e)))


import os


def appdir() -> str:
	return os.path.join(os.path.dirname(__file__), '../../')


def load_file(filename: str) -> str:
	filepath = os.path.join(appdir(), filename)
	with open(filepath) as f:
		return ''.join(f.readlines())


def parse_argv() -> dict[str, str]:
	import sys

	_, grammar, source = sys.argv
	return {'grammar': grammar, 'source': source}


def make_nodes(grammar: str, source: str) -> Nodes:
	from lark import Lark
	from lark.indenter import PythonIndenter

	parser = Lark(load_file(grammar), start='file_input', postlex=PythonIndenter(), parser='lalr')
	tree = parser.parse(load_file(source))
	return Nodes(tree, NodeResolver.load(make_settings()))


def make_context(source: str) -> Context:
	output = os.path.join(appdir(), f'{"/".join(source.split(".")[:-1])}.cpp')
	template_dir = os.path.join(appdir(), 'example/template')
	return Context(Registry(), Writer(output), Renderer(template_dir))


if __name__ == '__main__':
	args = parse_argv()
	nodes = make_nodes(args['grammar'], args['source'])
	ctx = make_context(args['source'])
	Runner(Handler()).run(nodes.by('file_input'), ctx)
