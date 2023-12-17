from typing import Generic, Iterator, TypedDict, TypeVar

from py2cpp.lang.error import stacktrace
from py2cpp.lang.eventemitter import EventEmitter, T_Callback
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.node.serializer import serialize
from py2cpp.view.render import Renderer, Writer

T_Node = TypeVar('T_Node', bound=Node)
T_Result = TypeVar('T_Result')

T_ArgumentVar = TypedDict('T_ArgumentVar', {'value': str})
T_DecoratorVar = TypedDict('T_DecoratorVar', {'symbol': str, 'arguments': list[T_ArgumentVar]})
T_ClassVar = TypedDict('T_ClassVar', {'class_name': str, 'decorators': list[T_DecoratorVar], 'parants': list[str]})
T_VariableVar = TypedDict('T_VariableVar', {'symbol': str, 'variable_type': str, 'value': str})
T_EnumVar = TypedDict('T_EnumVar', {'enum_name': str, 'variables': list[T_VariableVar]})
T_ParameterVar = TypedDict('T_ParameterVar', {'symbol': str, 'variable_type': str, 'default_value': str})
T_FunctionVar = TypedDict('T_FunctionVar', {'function_name': str, 'parameters': list[T_ParameterVar]})
T_MethodVar = TypedDict('T_MethodVar', {'function_name': str, 'class_name': str, 'parameters': list[T_ParameterVar]})
T_KeyValueVar = TypedDict('T_KeyValueVar', {'key': str, 'value': str})
T_DictVar = TypedDict('T_DictVar', {'items': list[T_KeyValueVar]})
T_ListVar = TypedDict('T_ListVar', {'values': list[str]})

T = TypeVar('T')


class Register(Generic[T]):
	def __init__(self) -> None:
		self.__stack: list[T] = []

	def push(self, entry: T) -> None:
		self.__stack.append(entry)

	def pop(self, entry_type: type[T]) -> T:
		return self.__stack.pop()

	def each_pop(self) -> Iterator[T]:
		for _ in range(len(self.__stack)):
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

	def on_file_input(self, node: defs.FileInput, ctx: Context) -> None:
		for _, statement in ctx.register.each_pop():
			ctx.writer.put(statement)

	def on_block(self, node: defs.Block, ctx: Context) -> None:
		text = ''
		for _, statement in ctx.register.each_pop():
			text += statement

		ctx.register.push((node, text))

	def on_class(self, node: defs.Class, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('class.j2', indent=node.nest, vars={**serialize(node, T_ClassVar), **{'block': block}})
		ctx.register.push((node, text))

	def on_enum(self, node: defs.Enum, ctx: Context) -> None:
		text = ctx.view.render('enum.j2', indent=node.nest, vars=serialize(node, T_EnumVar))
		ctx.register.push((node, text))

	def on_function(self, node: defs.Function, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('function.j2', indent=node.nest, vars={**serialize(node, T_FunctionVar), 'block': block})
		ctx.register.push((node, text))

	def on_constructor(self, node: defs.Constructor, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('constructur.j2', indent=node.nest, vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	def on_class_method(self, node: defs.ClassMethod, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('class_method.j2', indent=node.nest, vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	def on_method(self, node: defs.Method, ctx: Context) -> None:
		_, block = ctx.register.pop(tuple[defs.Block, str])
		text = ctx.view.render('method.j2', indent=node.nest, vars={**serialize(node, T_MethodVar), 'block': block})
		ctx.register.push((node, text))

	def on_move_assign(self, node: defs.MoveAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		text = ctx.view.render('move_assign.j2', indent=node.nest, vars={'symbol': symbol, 'value': value})
		ctx.register.push((node, text))

	def on_anno_assign(self, node: defs.AnnoAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		_, variable_type = ctx.register.pop(tuple[defs.Symbol, str])
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		text = ctx.view.render('anno_assign.j2', indent=node.nest, vars={'symbol': symbol, 'variable_type': variable_type, 'value': value})
		ctx.register.push((node, text))

	def on_aug_assign(self, node: defs.AugAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(tuple[defs.Symbol, str])
		_, operator = ctx.register.pop(tuple[defs.Terminal, str])
		_, value = ctx.register.pop(tuple[defs.Expression, str])
		text = ctx.view.render('aug_assign.j2', indent=node.nest, vars={'symbol': symbol, 'operator': operator, 'value': value})
		ctx.register.push((node, text))

	def on_import(self, node: defs.Import, ctx: Context) -> None:
		module_path = node.module_path.to_string()
		if module_path.startswith('py2cpp'):
			return

		text = ctx.view.render('import.j2', indent=node.nest, vars={'module_path': module_path})
		ctx.register.push((node, text))

	def on_dict(self, node: defs.Dict, ctx: Context) -> None:
		text = ctx.view.render('dict.j2', indent=node.nest, vars=serialize(node, T_DictVar))
		ctx.register.push((node, text))

	def on_list(self, node: defs.List, ctx: Context) -> None:
		text = ctx.view.render('list.j2', indent=node.nest, vars=serialize(node, T_ListVar))
		ctx.register.push((node, text))


class Runner:
	def __init__(self, handler: Handler) -> None:
		self.__handler = handler

	def run(self, root: Node, ctx: Context) -> None:
		try:
			ctx.on('action', self.__handler.on_action)

			for node in root.calculated():
				ctx.emit('action', node=node, ctx=ctx)

			ctx.writer.flush()

			ctx.off('action', self.__handler.on_action)
		except Exception as e:
			print(stacktrace(e))
