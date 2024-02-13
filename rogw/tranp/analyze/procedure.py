from typing import Callable, Generic, TypeVar, cast

from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
from rogw.tranp.lang.annotation import FunctionAnnotation
from rogw.tranp.node.node import Node

T_Ret = TypeVar('T_Ret')


class Procedure(Generic[T_Ret]):
	"""ASTプロシージャー。ASTの階層を辿って各エントリーを逐次処理し、最終的にルート要素のハンドラーで統合した単一の結果を出力する
	各処理はエントリーのNodeのclassificationに沿った名称でイベントハンドラーとして呼び出される

	Note:
		# イベントハンドラーの命名規則
		* enter: on_enter_${node.classification} ※未実装
		* action: on_${node.classification}
		* exit: on_exit_${node.classification}
	"""

	def __init__(self, verbose: bool = False) -> None:
		"""インスタンスを生成

		Args:
			verbose (bool): True = ログ出力
		"""
		self._stack: list[T_Ret] = []
		self.__invoker = HandlerInvoker[T_Ret]()
		self.__verbose = verbose

	def exec(self, root: Node) -> T_Ret:
		"""指定のルート要素から逐次処理し、結果を出力

		Args:
			root (Node): ルート要素
		Returns:
			T_Ret: 結果
		"""
		flatted = root.calculated()
		flatted.append(root)  # XXX 自身が含まれないので末尾に追加

		for node in flatted:
			self.process(node)

		return self.result()

	def result(self) -> T_Ret:
		"""結果を出力。結果は必ず1つでなければならない

		Returns:
			T_Ret: 結果
		Raises:
			LogicError: 結果が1つ以外。実装ミスと見做される
		"""
		if len(self._stack) != 1:
			raise LogicError(f'Invalid number of stacks. {len(self._stack)} != 1')

		return self._stack[-1]

	def process(self, node: Node) -> None:
		"""指定のノードのプロセス処理

		Args:
			node (Node): ノード
		"""
		self._enter(node)
		self._action(node)
		self._exit(node)

	def _action(self, node: Node) -> None:
		"""指定のノードのプロセス処理(本体)

		Args:
			node (Node): ノード
		Raises:
			LogicError: 対象ノードのハンドラーが未定義
		Note:
			ノード専用のハンドラーが未定義の場合はon_fallbackの呼び出しを試行する
		"""
		handler_name = f'on_{node.classification}'
		if hasattr(self, handler_name):
			self._run_action(node, handler_name)
		elif hasattr(self, 'on_fallback'):
			self._run_action(node, 'on_fallback')
		else:
			raise LogicError(f'Handler not defined. node: {str(node)}')

	def _enter(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行前) ※未実装

		Args:
			node (Node): ノード
		"""
		handler_name = f'on_enter_{node.classification}'
		if hasattr(self, handler_name):
			raise NotImplementedError()

	def _exit(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行後)

		Args:
			node (Node): ノード
		"""
		handler_name = f'on_exit_{node.classification}'
		if hasattr(self, handler_name):
			handler = cast(Callable[[Node, T_Ret], T_Ret], getattr(self, handler_name))
			self._stack.append(handler(node, self._stack.pop()))

	def _run_action(self, node: Node, handler_name: str) -> None:
		"""指定のノードのプロセス処理

		Args:
			node (Node): ノード
			handler_name (str): ハンドラー名
		"""
		before = len(self._stack)
		result = self.__invoker.invoke(getattr(self, handler_name), node, self._stack)
		consumed = len(self._stack)
		if result is not None:
			self._stack.append(result)

		self._log_action(node, handler_name, stacks=(before, consumed, len(self._stack)), result=result)

	def _log_action(self, node: Node, handler_name: str, stacks: tuple[int, int, int], result: T_Ret | None) -> None:
		"""プロセス処理のログを出力

		Args:
			node (Node): ノード
			handler_name (str): ハンドラー名
			stacks (tuple[int, int, int]): スタック数(実行前, 実行, 実行後)
			result (T_Ret | None): 結果
		"""
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
		"""ログ出力

		Args:
			*strs (str): 出力メッセージ
		"""
		if self.__verbose:
			print(*strs)  # FIXME impl Logger


class HandlerInvoker(Generic[T_Ret]):
	"""ハンドラー呼び出しユーティリティー"""

	def invoke(self, handler: Callable[..., T_Ret], node: Node, stack: list[T_Ret]) -> T_Ret | None:
		"""ハンドラーを呼び出す

		Args:
			handler (Callable[..., T_Ret]): ハンドラー
			node (Node): ノード
			stack (list[T_Ret]): スタック
		"""
		args = self.__invoke_args(handler, node, stack)
		return handler(**args)

	def __invoke_args(self, handler: Callable, node: Node, stack: list[T_Ret]) -> dict[str, Node | T_Ret | list[T_Ret]]:
		"""ハンドラーの引数をシグネチャーを元に解決

		Args:
			handler (Callable[..., T_Ret]): ハンドラー
			node (Node): ノード
			stack (list[T_Ret]): スタック
		Returns:
			dict[str, Node | T_Ret | list[T_Ret]]
		"""
		func_anno = FunctionAnnotation(handler)
		args: dict[str, Node | T_Ret | list[T_Ret]] = {}
		args_anno = func_anno.args
		args_keys = reversed(args_anno.keys())
		for key in args_keys:
			arg_anno = args_anno[key]
			if arg_anno.is_list:
				args[key] = self.__pluck_values(stack, node, key)
			elif issubclass(arg_anno.org_type, Node):
				args[key] = node
			else:
				args[key] = self.__pluck_value(stack)

		return args

	def __pluck_values(self, stack: list[T_Ret], node: Node, key: str) -> list[T_Ret]:
		"""リストの引数をスタックから引き出す。要素数はノードの対象プロパティーの要素数を元に決定

		Args:
			stack (list[T_Ret]): スタック
			node (Node): ノード
			key (str): プロパティー名
		Returns:
			list[T_Ret]: リストの引数
		"""
		counts = len(getattr(node, key))
		args = [stack.pop() for _ in range(counts)]
		return list(reversed(args))

	def __pluck_value(self, stack: list[T_Ret]) -> T_Ret:
		"""引数をスタックから引き出す

		Args:
			stack (list[T_Ret]): スタック
		Returns:
			T_Ret: 引数
		"""
		return stack.pop()
