from typing import Any, Callable, Generic, TypeVar, cast

from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
from rogw.tranp.lang.eventemitter import EventEmitter
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
		self.__stack: list[T_Ret] = []
		self.__verbose = verbose
		self.__emitter = EventEmitter[T_Ret]()

	def on(self, action: str, handler: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): アクション名
			handler (Callable[..., T_Ret]): ハンドラー
		"""
		self.__emitter.on(action, handler)

	def off(self, action: str, handler: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): アクション名
			handler (Callable[..., T_Ret]): ハンドラー
		"""
		self.__emitter.off(action, handler)

	def clear_handler(self) -> None:
		"""イベントハンドラーの登録を全て解除"""
		self.__emitter.clear()

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
			self.__process(node)

		return self.__result()

	def __result(self) -> T_Ret:
		"""結果を出力。結果は必ず1つでなければならない

		Returns:
			T_Ret: 結果
		Raises:
			LogicError: 結果が1つ以外。実装ミスと見做される
		"""
		if len(self.__stack) != 1:
			raise LogicError(f'Invalid number of stacks. {len(self.__stack)} != 1')

		return self.__stack.pop()

	def __process(self, node: Node) -> None:
		"""指定のノードのプロセス処理

		Args:
			node (Node): ノード
		"""
		self.__enter(node)
		self.__action(node)
		self.__exit(node)

	def __action(self, node: Node) -> None:
		"""指定のノードのプロセス処理(本体)

		Args:
			node (Node): ノード
		Raises:
			LogicError: 対象ノードのハンドラーが未定義
		Note:
			ノード専用のハンドラーが未定義の場合はon_fallbackの呼び出しを試行する
		"""
		handler_name = f'on_{node.classification}'
		if self.__emitter.observed(handler_name):
			self.__run_action(node, handler_name)
		elif self.__emitter.observed('on_fallback'):
			self.__run_action(node, 'on_fallback')
		else:
			raise LogicError(f'Handler not defined. node: {str(node)}')

	def __enter(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行前)

		Args:
			node (Node): ノード
		Raises:
			LogicError: 入力と出力が不一致
		"""
		handler_name = f'on_enter_{node.classification}'
		if not self.__emitter.observed(handler_name):
			return

		begin = len(self.__stack)
		event = self.__make_event(node)
		consumed = len(self.__stack)
		result = self.__emit_proxy(handler_name, node, **event)
		results = cast(list[T_Ret], result)  # FIXME 公開しているイベントハンドラーの定義と異なる形式を期待
		if (begin - consumed) != len(results):
			raise LogicError(f'Result not match. node: {node}, event: {begin - consumed}, results: {len(results)}')

		self.__stack.extend(reversed(results))

	def __exit(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行後)

		Args:
			node (Node): ノード
		Raises:
			LogicError: 不正な結果(None)
		"""
		handler_name = f'on_exit_{node.classification}'
		if not self.__emitter.observed(handler_name):
			return

		org_result = self.__stack_pop()
		new_result = self.__emit_proxy(handler_name, node, result=org_result)
		if new_result is None:
			raise LogicError('Result is null.')

		self.__stack.append(new_result)

	def __run_action(self, node: Node, handler_name: str) -> None:
		"""指定のノードのプロセス処理

		Args:
			node (Node): ノード
			handler_name (str): ハンドラー名
		"""
		before = len(self.__stack)
		result = self.__emit_proxy(handler_name, node, **self.__make_event(node))
		consumed = len(self.__stack)
		if result is not None:
			self.__stack.append(result)

		self.__put_log_action(node, handler_name, stacks=(before, consumed, len(self.__stack)), result=result)

	def __emit_proxy(self, action: str, node: Node, **event: T_Ret | list[T_Ret]) -> T_Ret | None:
		"""イベント発火プロクシー

		Args:
			action (str): イベント名
			node (Node): ノード
			**event (T_Ret | list[T_Ret]): イベントデータ
		Returns:
			T_Ret | None: 結果
		Raises:
			LogicError: イベントデータが不正
		"""
		try:
			return self.__emitter.emit(action, node=node, **event)
		except TypeError as e:
			raise LogicError(f'Invalid event schema. node: {node}, props: {node.prop_keys()}, event: {event}') from e

	def __make_event(self, node: Node) -> dict[str, T_Ret | list[T_Ret]]:
		"""ノードの展開プロパティーを元にイベントデータを生成

		Args:
			node (Node): ノード
		Returns:
			dict[str, Node | T_Ret | list[T_Ret]]: イベントデータ
		"""
		event: dict[str, T_Ret | list[T_Ret]] = {}
		prop_keys = reversed(node.prop_keys())
		for prop_key in prop_keys:
			if self.__is_prop_list_by(node, prop_key):
				counts = len(getattr(node, prop_key))
				event[prop_key] = list(reversed([self.__stack_pop() for _ in range(counts)]))
			else:
				event[prop_key] = self.__stack_pop()

		return event

	def __is_prop_list_by(self, node: Node, prop_key: str) -> bool:
		"""展開プロパティーがリストか判定

		Args:
			node (Node): ノード
			prop_key (str): プロパティー名
		Returns:
			bool: True = リスト, False = 単体
		"""
		prop_anno = getattr(node.__class__, prop_key).fget.__annotations__['return']
		return hasattr(prop_anno, '__origin__') and prop_anno.__origin__ is list

	def __stack_pop(self) -> T_Ret:
		"""スタックから結果を取得

		Returns:
			T_Ret: 結果
		Raises:
			LogicError: スタックが不足
		"""
		if self.__stack:
			return self.__stack.pop()

		raise LogicError('Stack is empty.')

	def __put_log_action(self, node: Node, handler_name: str, stacks: tuple[int, int, int], result: T_Ret | None) -> None:
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
		self.__put_log(f'{indent} {joined_data}')

	def __put_log(self, *strs: str) -> None:
		"""ログ出力

		Args:
			*strs (str): 出力メッセージ
		"""
		if self.__verbose:
			print(*strs)  # FIXME impl Logger
