from typing import Generic, Iterator, TypedDict, TypeVar

from py2cpp.errors import LogicError
from py2cpp.lang.error import stacktrace
from py2cpp.lang.eventemitter import EventEmitter, T_Callback
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.serializer import serialize
from py2cpp.view.render import Renderer, Writer

T_Node = TypeVar('T_Node', bound=Node)
T_Result = TypeVar('T_Result')

T_ArgumentVar = TypedDict('T_ArgumentVar', {'value': str})
T_DecoratorVar = TypedDict('T_DecoratorVar', {'symbol': str, 'arguments': list[T_ArgumentVar]})
T_ClassVar = TypedDict('T_ClassVar', {'class_name': str, 'decorators': list[T_DecoratorVar], 'parents': list[str]})
T_VariableVar = TypedDict('T_VariableVar', {'symbol': str, 'variable_type': str, 'value': str})
T_MoveAssignVar = TypedDict('T_VariableVar', {'symbol': str, 'value': str})
T_EnumVar = TypedDict('T_EnumVar', {'enum_name': str, 'variables': list[T_MoveAssignVar]})  # XXX 一旦MoveAssignで妥協
T_ParameterVar = TypedDict('T_ParameterVar', {'symbol': str, 'variable_type': str, 'default_value': str})
T_FunctionVar = TypedDict('T_FunctionVar', {'function_name': str, 'parameters': list[T_ParameterVar]})
T_MethodVar = TypedDict('T_MethodVar', {'access': str, 'function_name': str, 'class_name': str, 'parameters': list[T_ParameterVar]})
T_KeyValueVar = TypedDict('T_KeyValueVar', {'key': str, 'value': str})
T_DictVar = TypedDict('T_DictVar', {'items': list[T_KeyValueVar]})
T_ListVar = TypedDict('T_ListVar', {'values': list[str]})

T = TypeVar('T')


class Register(Generic[T]):
	def __init__(self) -> None:
		self.__stack: list[T] = []

	def __len__(self) -> int:
		return len(self.__stack)

	def push(self, entry: T) -> None:
		self.__stack.append(entry)

	def pop(self, entry_type: type[T]) -> T:
		return self.__stack.pop()

	def each_pop(self, counts: int = 0) -> Iterator[T]:
		if counts < 0 or len(self) < counts:
			raise LogicError(counts, len(self))

		loops = len(self) if counts == 0 else counts
		for _ in range(loops):
			yield self.__stack.pop()


class Context:
	def __init__(self, register: Register[tuple[Node, str]], writer: Writer, view: Renderer) -> None:
		self.__emitter = EventEmitter()
		self.register = register
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
		handler_name = f'on_{node.identifer}'
		if hasattr(self, handler_name):
			getattr(self, handler_name)(node, ctx)
		else:
			self.on_terminal(node, ctx)

	# General

	def on_file_input(self, node: defs.FileInput, ctx: Context) -> None:
		statements = [statement for _, statement in ctx.register.each_pop()]
		statements.reverse()
		text = ctx.view.render('block.j2', vars={'statements': statements})
		ctx.writer.put(text)

	# Common

	def on_block(self, node: defs.Block, ctx: Context) -> None:
		statements = [statement for _, statement in ctx.register.each_pop(len(node.statements))]
		statements.reverse()
		text = ctx.view.render('block.j2', vars={'statements': statements})
		ctx.register.push((node, text))

	# Statement - simple

	def on_move_assign(self, node: defs.MoveAssign, ctx: Context) -> None:
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		text = ctx.view.render('move_assign.j2', vars={'symbol': symbol, 'value': value})
		ctx.register.push((node, text))

	def on_anno_assign(self, node: defs.AnnoAssign, ctx: Context) -> None:
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		_, variable_type = ctx.register.pop(tuple[defs.Symbol, str])
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		text = ctx.view.render('anno_assign.j2', vars={'symbol': symbol, 'variable_type': variable_type, 'value': value})
		ctx.register.push((node, text))

	def on_aug_assign(self, node: defs.AugAssign, ctx: Context) -> None:
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		_, operator = ctx.register.pop(tuple[defs.Terminal, str])
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		text = ctx.view.render('aug_assign.j2', vars={'symbol': symbol, 'operator': operator, 'value': value})
		ctx.register.push((node, text))

	def on_return(self, node: defs.Return, ctx: Context) -> None:
		_, return_value = ctx.register.pop(tuple[defs.Expression, str])
		text = ctx.view.render('return.j2', vars={'return_value': return_value})
		ctx.register.push((node, text))

	def on_import(self, node: defs.Import, ctx: Context) -> None:
		module_path = node.module_path.to_string()
		if module_path.startswith('py2cpp'):
			return

		text = ctx.view.render('import.j2', vars={'module_path': module_path})
		ctx.register.push((node, text))

	# Statement - compound

	def on_class(self, node: defs.Class, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('class.j2', vars={**serialize(node, T_ClassVar), **{'block': block}})
		ctx.register.push((node, text))

	def on_enum(self, node: defs.Enum, ctx: Context) -> None:
		text = ctx.view.render('enum.j2', vars=serialize(node, T_EnumVar))
		ctx.register.push((node, text))

	def on_function(self, node: defs.Function, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('function.j2', vars={**serialize(node, T_FunctionVar), 'block': block})
		ctx.register.push((node, text))

	def on_constructor(self, node: defs.Constructor, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('constructor.j2', vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	def on_class_method(self, node: defs.ClassMethod, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('class_method.j2', vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	def on_method(self, node: defs.Method, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('method.j2', vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	# Function/Class Elements

	def on_argument(self, node: defs.Argument, ctx: Context) -> None:
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		ctx.register.push((node, value))

	# Primary

	def on_func_call(self, node: defs.FuncCall, ctx: Context) -> None:
		arguments = [argument for _, argument in ctx.register.each_pop(len(node.arguments))]
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		text = ctx.view.render('func_call.j2', vars={'symbol': symbol, 'arguments': arguments})
		ctx.register.push((node, text))

	# Literal

	def on_dict(self, node: defs.Dict, ctx: Context) -> None:
		text = ctx.view.render('dict.j2', vars=serialize(node, T_DictVar))
		ctx.register.push((node, text))

	def on_list(self, node: defs.List, ctx: Context) -> None:
		text = ctx.view.render('list.j2', vars=serialize(node, T_ListVar))
		ctx.register.push((node, text))

	# Terminal

	def on_terminal(self, node: Node, ctx: Context) -> None:
		ctx.register.push((node, node.to_string()))


class Runner:
	def __init__(self, handler: Handler) -> None:
		self.__handler = handler

	def run(self, root: Node, ctx: Context) -> None:
		try:
			ctx.on('action', self.__handler.on_action)

			for node in root.calculated():
				print('action:', str(node))
				ctx.emit('action', node=node, ctx=ctx)

			ctx.emit('action', node=root, ctx=ctx)  # FIXME
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
	return Nodes(tree, NodeResolver.load(Settings(
		symbols={
			# General
			'file_input': defs.FileInput,
			# Common
			'block': defs.Block,
			'decorator': defs.Decorator,
			# Statement - simple
			'assign_stmt': defs.Assign,
			'return_stmt': defs.Return,
			'import_stmt': defs.Import,
			# Statement - compound
			'if_stmt': defs.If,
			'class_def': defs.Class,
			'enum_def': defs.Enum,
			'function_def': defs.Function,
			# Function/Class Elements
			'paramvalue': defs.Parameter,
			'argvalue': defs.Argument,
			# Primary
			'getattr': defs.Symbol,
			'funccall': defs.FuncCall,
			# Literal
			'dict': defs.Dict,
			'list': defs.List,
			'integer': defs.Integer,
			'float': defs.Float,
			'string': defs.List,
			# Terminal
			'__empty__': defs.Empty,
		},
		fallback=defs.Terminal
	)))


def make_context(source: str) -> Context:
	output = os.path.join(appdir(), f'{"/".join(source.split(".")[:-1])}.cpp')
	template_dir = os.path.join(appdir(), 'example/template')
	return Context(Register(), Writer(output), Renderer(template_dir))


if __name__ == '__main__':
	args = parse_argv()
	nodes = make_nodes(args['grammar'], args['source'])
	ctx = make_context(args['source'])
	Runner(Handler()).run(nodes.by('file_input'), ctx)
