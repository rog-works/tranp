from typing import Any, Iterator, TypedDict, TypeVar, cast

from py2cpp.errors import LogicError
from py2cpp.lang.error import stacktrace
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.lang.eventemitter import EventEmitter, T_Callback

T_Node = TypeVar('T_Node', bound=Node)
T_Result = TypeVar('T_Result')

T_ArgumentVar = TypedDict('T_ArgumentVar', {'value': str})
T_DecoratorVar = TypedDict('T_DecoratorVar', {'symbol': str, 'arguments': list[T_ArgumentVar]})
T_ClassVar = TypedDict('T_ClassVar', {'class_name': str, 'decorators': list[T_DecoratorVar], 'parants': list[str]})
T_VariableVar = TypedDict('T_VariableVar', {'symbol': str, 'variable_type': str, 'value': str})
T_EnumVar = TypedDict('T_EnumVar', {'enum_name': str, 'variables': list[T_VariableVar]})
T_ParameterVar = TypedDict('T_ParameterVar', {'symbol': str, 'variable_type': str, 'default_value': str})
T_FunctionVar = TypedDict('T_FunctionVar', {'function_name': str, 'class_name': str, 'parameters': list[T_ParameterVar]})
T_KeyValueVar = TypedDict('T_DictVar', {'key': str, 'value': str})
T_DictVar = TypedDict('T_DictVar', {'items': list[T_KeyValueVar]})
T_ListVar = TypedDict('T_DictVar', {'values': list[str]})

T = TypeVar('T')


def serialize(data: Node, schema: type[T]) -> T:
	out = {}
	for prop_key, prop_type in schema.__annotations__.items():
		prop_schema = schema.__annotations__[prop_key]
		if prop_type is list:
			out[prop_key] = []
			elem_schema = prop_schema.__args__[0]
			for elem in getattr(data, prop_key):
				out[prop_key].append(serialize(elem, elem_schema))
		elif prop_type is dict:
			out[prop_key] = {}
			for in_key, in_value in getattr(data, prop_key).items():
				elem_schema = prop_schema.__annotations__[in_key]
				out[prop_key][in_key] = serialize(in_value, elem_schema)
		elif prop_type is str:
			out[prop_key] = getattr(data, prop_key).to_string()
		else:
			raise LogicError(data, schema, prop_key, prop_type)

	return cast(T, out)


class Register:
	def __init__(self) -> None:
		self.__stack: list[tuple[Node, Any]] = []

	def push(self, node: Node, result: Any) -> None:
		self.__stack.append((node, result))

	def pop(self, node_type: type[T_Node], result_type: type[T_Result]) -> tuple[T_Node, T_Result]:
		return cast(tuple[node_type, result_type], self.__stack.pop())

	def __iter__(self) -> Iterator[tuple[Node, Any]]:
		for _ in range(len(self.__stack)):
			yield self.__stack.pop()


class Writer:
	def __init__(self, filepath: str) -> None:
		self.__filepath = filepath
		self.__content = ''

	def put(self, text: str) -> None:
		self.__content += text

	def flush(self) -> None:
		with open(self.__filepath, mode='wb') as f:
			f.write(self.__content.encode('utf-8'))


class View:
	def render(self, template: str, indent: int, vars: TypedDict | dict[str, str], **other_vars: str) -> str:
		...

	def indentation(self, text: str, indent: int) -> str:
		begin = ''.join(['\t' for _ in range(indent)])
		return f'\n{begin}'.join(text.split('\n'))


class Context:
	def __init__(self, register: Register, writer: Writer, view: View) -> None:
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
		for _, statement in ctx.register:
			ctx.writer.put(statement)

	def on_block(self, node: defs.Block, ctx: Context) -> None:
		text = ''
		for _, statement in ctx.register:
			text += statement

		ctx.register.push(node, text)

	def on_class(self, node: defs.Class, ctx: Context) -> None:
		_, block = ctx.register.pop(defs.Block, str)
		text = ctx.view.render('class.j2', node.nest, serialize(node, T_ClassVar), block=block)
		ctx.register.push(node, text)

	def on_enum(self, node: defs.Enum, ctx: Context) -> None:
		text = ctx.view.render('enum.j2', node.nest, serialize(node, T_EnumVar))
		ctx.register.push(node, text)

	def on_constructor(self, node: defs.Constructor, ctx: Context) -> None:
		_, block = ctx.register.pop(defs.Block, str)
		text = ctx.view.render('constructur.j2', node.nest, serialize(node, T_FunctionVar), block=block)
		ctx.register.push(node, text)

	def on_class_method(self, node: defs.ClassMethod, ctx: Context) -> None:
		_, block = ctx.register.pop(defs.Block, str)
		text = ctx.view.render('class_method.j2', node.nest, serialize(node, T_FunctionVar), block=block)
		ctx.register.push(node, text)

	def on_method(self, node: defs.Method, ctx: Context) -> None:
		_, block = ctx.register.pop(defs.Block, str)
		text = ctx.view.render('method.j2', node.nest, serialize(node, T_FunctionVar), block=block)
		ctx.register.push(node, text)

	def on_function(self, node: defs.Function, ctx: Context) -> None:
		_, block = ctx.register.pop(defs.Block, str)
		text = ctx.view.render('function.j2', node.nest, serialize(node, T_FunctionVar), block=block)
		ctx.register.push(node, text)

	def on_move_assign(self, node: defs.MoveAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(defs.Symbol, str)
		_, value = ctx.register.pop(defs.Expression, str)
		vars = {'symbol': symbol, 'value': value}
		text = ctx.view.render('move_assign.j2', node.nest, vars)
		ctx.register.push(node, text)

	def on_anno_assign(self, node: defs.AnnoAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(defs.Symbol, str)
		_, variable_type = ctx.register.pop(defs.Symbol, str)
		_, value = ctx.register.pop(defs.Expression, str)
		vars = {'symbol': symbol, 'variable_type': variable_type, 'value': value}
		text = ctx.view.render('anno_assign.j2', node.nest, vars)
		ctx.register.push(node, text)

	def on_aug_assign(self, node: defs.AugAssign, ctx: Context) -> None:
		_, symbol = ctx.register.pop(defs.Symbol, str)
		_, operator = ctx.register.pop(defs.Terminal, str)
		_, value = ctx.register.pop(defs.Expression, str)
		vars = {'symbol': symbol, 'operator': operator, 'value': value}
		text = ctx.view.render('aug_assign.j2', node.nest, vars)
		ctx.register.push(node, text)

	def on_import(self, node: defs.Import, ctx: Context) -> None:
		module_path = node.module_path.to_string()
		if module_path.startswith('py2cpp'):
			return

		vars = {'module_path': module_path}
		text = ctx.view.render('import.j2', node.nest, vars)
		ctx.register.push(node, text)

	def on_dict(self, node: defs.Dict, ctx: Context) -> None:
		text = ctx.view.render('dict.j2', node.nest, serialize(node, T_DictVar))
		ctx.register.push(node, text)

	def on_list(self, node: defs.List, ctx: Context) -> None:
		text = ctx.view.render('list.j2', node.nest, serialize(node, T_ListVar))
		ctx.register.push(node, text)


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
