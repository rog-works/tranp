from typing import Callable, Generic, TypeVar, cast

from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.annotation import FunctionAnnotation
from py2cpp.node.node import Node

T_Ret = TypeVar('T_Ret')


class Procedure(Generic[T_Ret]):
	def __init__(self, verbose: bool = False) -> None:
		self._stack: list[T_Ret] = []
		self.__invoker = HandlerInvoker[T_Ret]()
		self.__verbose = verbose

	def result(self) -> T_Ret:
		if len(self._stack) != 1:
			raise LogicError(f'Invalid number of stacks. {len(self._stack)} != 1')

		return self._stack.pop()

	def process(self, node: Node) -> None:
		self._enter(node)
		self._action(node)
		self._exit(node)

	def _action(self, node: Node) -> None:
		handler_name = f'on_{node.classification}'
		if hasattr(self, handler_name):
			self._run_action(handler_name, node)
		elif hasattr(self, 'on_fallback'):
			self._run_action('on_fallback', node)
		else:
			raise LogicError(f'Handler not defined. node: {str(node)}')

	def _enter(self, node: Node) -> None:
		handler_name = f'on_enter_{node.classification}'
		if hasattr(self, handler_name):
			# FIXME impl?
			raise NotImplementedError()

	def _exit(self, node: Node) -> None:
		handler_name = f'on_exit_{node.classification}'
		if hasattr(self, handler_name):
			handler = cast(Callable[[Node, T_Ret], T_Ret], getattr(self, handler_name))
			self._stack.append(handler(node, self._stack.pop()))

	def _run_action(self, handler_name: str, node: Node) -> None:
		before = len(self._stack)
		result = self.__invoker.invoke(getattr(self, handler_name), node, self._stack)
		consumed = len(self._stack)
		if result is not None:
			self._stack.append(result)

		self._log_action(handler_name, node, stacks=(before, consumed, len(self._stack)), result=result)

	def _log_action(self, handler_name: str, node: Node, stacks: tuple[int, int, int], result: T_Ret | None) -> None:
		result_str = str(result).replace('\n', '\\n')
		indent = ' ' * DSN.elem_counts(node.full_path)
		data = {
			str(node): handler_name,
			'stacks': ' -> '.join(map(str, stacks)),
			'result': result_str if len(result_str) < 50 else f'{result_str[:50]}...',
		}
		joined_data = ', '.join([f'{key}: {value}' for key, value in data.items()])
		self._log(f'{indent} {joined_data}')

	def _log(self, *strs: str) -> None:
		if self.__verbose:
			print(*strs)  # FIXME impl Logger


class HandlerInvoker(Generic[T_Ret]):
	def invoke(self, handler: Callable[..., T_Ret], node: Node, stack: list[T_Ret]) -> T_Ret | None:
		args = self.__invoke_args(handler, node, stack)
		return handler(**args)

	def __invoke_args(self, handler: Callable, node: Node, stack: list[T_Ret]) -> dict[str, Node | T_Ret | list[T_Ret]]:
		func_anno = FunctionAnnotation(handler)
		args: dict[str, Node | T_Ret | list[T_Ret]] = {}
		args_anno = func_anno.args
		args_keys = reversed(args_anno.keys())
		for key in args_keys:
			arg_anno = args_anno[key]
			try:
				if arg_anno.is_list:
					args[key] = self.__pluck_values(stack, node, key)
				elif issubclass(arg_anno.org_type, Node):
					args[key] = node
				else:
					args[key] = self.__pluck_value(stack)
			except TypeError as e:
				print(node, key, e)

		return args

	def __pluck_values(self, stack: list[T_Ret], node: Node, key: str) -> list[T_Ret]:
		counts = len(getattr(node, key))
		args = [stack.pop() for _ in range(counts)]
		return list(reversed(args))

	def __pluck_value(self, stack: list[T_Ret]) -> T_Ret:
		return stack.pop()
