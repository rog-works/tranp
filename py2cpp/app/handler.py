from py2cpp.node.definition import Class
from py2cpp.node.node import Node
from py2cpp.lang.eventemitter import EventEmitter, T_Callback


class Context:
	def __init__(self) -> None:
		self.__emitter = EventEmitter()


	def emit(self, action: str, **kwargs) -> None:
		self.__emitter.emit(action, **kwargs)


	def on(self, action: str, callback: T_Callback) -> None:
		self.__emitter.on(action, callback)


	def off(self, action: str, callback: T_Callback) -> None:
		self.__emitter.off(action, callback)


class Handler:
	def on_action(self, node: Node, ctx: Context) -> None:
		if hasattr(self, node.tag):
			getattr(self, node.tag)(node, ctx)


	def fild_input(self, node: Node, ctx: Context) -> None:
		pass


	def class_def(self, node: Class, ctx: Context) -> None:
		pass


class Runner:
	def run(self, root: Node) -> None:
		handler = Handler()
		ctx = Context()
		ctx.on('action', handler.on_action)

		for node in root.flatten():
			ctx.emit('action', node=node, ctx=ctx)
