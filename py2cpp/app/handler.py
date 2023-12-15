from typing import Any

from py2cpp.node.definition import (
	AnnoAssign,
	Assign,
	AugAssign,
	Class,
	ClassMethod,
	Constructor,
	Dict,
	Function,
	Enum,
	Import,
	List,
	Method,
	MoveAssign,
)
from py2cpp.node.node import Node
from py2cpp.lang.eventemitter import EventEmitter, T_Callback


class Writer:
	@property
	def cursor(self) -> int:
		...


	def put(self, text: str) -> None:
		...


	def line(self, text: str) -> None:
		...


	def push(self) -> 'Writer':
		...


	def pop(self) -> 'Writer':
		...


	def begin(self, offset: int = 0) -> None:
		...


	def seek(self, offset: int = 0) -> None:
		...


	def end(self, offset: int = 0) -> None:
		...


	def render(self, template: str, vars: dict[str, Any]) -> str:
		...


class Context:
	def __init__(self) -> None:
		self.__emitter = EventEmitter()
		self.writer = Writer()
		self.nest = 0


	def emit(self, action: str, **kwargs) -> None:
		self.__emitter.emit(action, **kwargs)


	def on(self, action: str, callback: T_Callback) -> None:
		self.__emitter.on(action, callback)


	def off(self, action: str, callback: T_Callback) -> None:
		self.__emitter.off(action, callback)


class Handler:
	def on_action(self, node: Node, ctx: Context) -> None:
		self.indentation(node, ctx)

		if hasattr(self, node.tag):
			getattr(self, node.tag)(node, ctx)


	def indentation(self, node: Node, ctx: Context) -> None:
		if ctx.nest < node.nest:
			ctx.writer.push()

		if ctx.nest > node.nest:
			ctx.writer.pop()

		ctx.nest = node.nest


	def class_def(self, node: Class, ctx: Context) -> None:
		text = ctx.writer.render('class.j2', {
			'class_name': node.class_name.to_string(),
			'decorators': [
				{
					'symbol': decorator.symbol.to_string(),
					'arguments': [
						{'value': argument.value.to_string()}
						for argument in decorator.arguments
					],
				}
				for decorator in node.decorators
			],
			'parents': [parent.to_string() for parent in node.parents],
		})
		cursor = text.find('@cursor@')
		ctx.writer.put(text)
		ctx.writer.seek(cursor)


	def enum_def(self, node: Enum, ctx: Context) -> None:
		text = ctx.writer.render('enum.j2', {
			'enum_name': node.enum_name.to_string(),
			'variables': [
				{
					'symbol': variable.symbol.to_string(),
					'value': variable.value.to_string(),
				}
				for variable in node.variables
			],
		})
		ctx.writer.put(text)


	def function_def(self, node: Function, ctx: Context) -> None:
		template = ''
		if isinstance(node, Constructor):
			template = 'constructor.j2'
		elif isinstance(node, ClassMethod):
			template = 'class_method.j2'
		elif isinstance(node, Method):
			template = 'method.j2'

		text = ctx.writer.render(template, {
			'access': node.access,
			'class_name': '',  # FIXME
			'parameters': [
				{
					'param_symbol': parameter.param_symbol,
					'param_type': parameter.param_type,
					'default_value': parameter.default_value,
				}
				for parameter in node.parameters
			],
		})

		cursor = text.find('@cursor@')
		ctx.writer.put(text)
		ctx.writer.seek(cursor)


	def assign_stmt(self, node: Assign, ctx: Context) -> None:
		text = ''
		if isinstance(node, MoveAssign):
			text = ctx.writer.render('move_assign.j2', {
				'symbol': node.symbol.to_string(),
				'value': node.value.to_string(),
			})
		elif isinstance(node, AnnoAssign):
			text = ctx.writer.render('anno_assign.j2', {
				'symbol': node.symbol.to_string(),
				'variable_type': node.variable_type.to_string(),
				'value': node.value.to_string(),
			})
		elif isinstance(node, AugAssign):
			text = ctx.writer.render('aug_assign.j2', {
				'symbol': node.symbol.to_string(),
				'operator': node.operator.to_string(),
				'value': node.value.to_string(),
			})

		ctx.writer.put(text)


	def import_stmt(self, node: Import, ctx: Context) -> None:
		module_path = node.module_path.to_string()
		if module_path.startswith('py2cpp'):
			return

		text = ctx.writer.render('import.j2', {'module_path': module_path})
		ctx.writer.put(text)


	def dict_(self, node: Dict, ctx: Context) -> None:
		text = ctx.writer.render('dict.j2', {'items': {item.key.to_string(): item.value.to_string() for item in node.items}})
		ctx.writer.put(text)


class Runner:
	def run(self, root: Node) -> None:
		handler = Handler()
		ctx = Context()
		ctx.on('action', handler.on_action)

		for node in root.flatten():
			ctx.emit('action', node=node, ctx=ctx)
