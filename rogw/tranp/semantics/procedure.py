from typing import Generic, TypeVar, cast

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.eventemitter import Callback, EventEmitter, Observable
from rogw.tranp.syntax.node.node import Node

T_Ret = TypeVar('T_Ret')


class Procedure(Generic[T_Ret]):
	"""ASTプロシージャー。ASTの階層を辿って各エントリーを逐次処理し、最終的にルート要素のハンドラーで統合した単一の結果を出力する
	各処理はエントリーのNodeのclassificationに沿った名称でイベントハンドラーとして呼び出される

	Note:
		```
		### イベントハンドラーの命名規則
		* enter: on_enter_${node.classification} ※未実装
		* action: on_${node.classification}
		* exit: on_exit_${node.classification}
		```
	"""

	def __init__(self, verbose: bool = False) -> None:
		"""インスタンスを生成

		Args:
			verbose: True = ログ出力
		"""
		self.__stacks: list[list[T_Ret]] = []
		self.__verbose = verbose
		self.__emitter = EventEmitter[T_Ret]()

	@duck_typed(Observable)
	def on(self, action: str, callback: Callback[T_Ret]) -> None:
		"""イベントハンドラーを登録

		Args:
			action: アクション名
			callback: ハンドラー
		"""
		self.__emitter.on(action, callback)

	@duck_typed(Observable)
	def off(self, action: str, callback: Callback[T_Ret]) -> None:
		"""イベントハンドラーを解除

		Args:
			action: アクション名
			callback: ハンドラー
		"""
		self.__emitter.off(action, callback)

	def clear_handler(self) -> None:
		"""イベントハンドラーの登録を全て解除"""
		self.__emitter.clear()

	def exec(self, root: Node) -> T_Ret:
		"""指定のルート要素から逐次処理し、結果を出力

		Args:
			root: ルート要素
		Returns:
			結果
		Note:
			実行処理はスタックされるため、このメソッドを再帰的に実行した場合でも順次解決される
		Raises:
			Errors.Error: 実行中のエラー
		"""
		self.__stacks.append([])
		result = self.__exec_impl(root)
		self.__stacks.pop()
		return result

	def __exec_impl(self, root: Node) -> T_Ret:
		"""指定のルート要素から逐次処理し、結果を出力

		Args:
			root: ルート要素
		Returns:
			結果
		Raises:
			Errors.Logic: スタック数が不正(1以外)
			Errors.Error: 実行中のエラー
		"""
		try:
			flatted = root.procedural()
			flatted.append(root)  # XXX 自身が含まれないので末尾に追加

			for node in flatted:
				self.__process(node)

			return self.__result()
		except AssertionError:
			raise Errors.Logic(root, len(self.__stack), 'Invalid number of stacks')

	@property
	def __stack(self) -> list[T_Ret]:
		"""Returns: 実行中のスタック"""
		return self.__stacks[-1]

	def __result(self) -> T_Ret:
		"""結果を出力。結果は必ず1つでなければならない

		Returns:
			結果
		Raises:
			AssertionError: 結果が1以外。実装ミス
		"""
		assert len(self.__stack) == 1
		return self.__stack.pop()

	def __process(self, node: Node) -> None:
		"""指定のノードのプロセス処理

		Args:
			node: ノード
		"""
		self.__enter(node)
		self.__action(node)
		self.__exit(node)

	def __action(self, node: Node) -> None:
		"""指定のノードのプロセス処理(本体)

		Args:
			node: ノード
		Raises:
			Errors.MustBeImplemented: 対象ノードのハンドラーが未定義
		Note:
			ノード専用のハンドラーが未定義の場合はon_fallbackの呼び出しを試行する
		"""
		handler_name = f'on_{node.classification}'
		if self.__emitter.observed(handler_name):
			self.__run_action(node, handler_name)
		elif self.__emitter.observed('on_fallback'):
			self.__run_action(node, 'on_fallback')
		else:
			raise Errors.MustBeImplemented(node, 'Handler not defined')

	def __enter(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行前)

		Args:
			node: ノード
		Raises:
			Errors.Logic: 入力と出力が不一致
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
			raise Errors.Logic(node, begin - consumed, len(results), 'Result not match')

		self.__stack.extend(results)

	def __exit(self, node: Node) -> None:
		"""指定のノードのプロセス処理(実行後)

		Args:
			node: ノード
		Raises:
			Errors.Logic: 結果がNone
		"""
		handler_name = f'on_exit_{node.classification}'
		if not self.__emitter.observed(handler_name):
			return

		org_result = self.__stack_pop()
		new_result = self.__emit_proxy(handler_name, node, result=org_result)
		if new_result is None:
			raise Errors.Logic(node, 'Result is null')

		self.__stack.append(new_result)

	def __run_action(self, node: Node, handler_name: str) -> None:
		"""指定のノードのプロセス処理

		Args:
			node: ノード
			handler_name: ハンドラー名
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
			action: イベント名
			node: ノード
			**event: イベントデータ
		Returns:
			結果
		Raises:
			Errors.InvalidSchema: イベントデータとハンドラーの引数が不一致
			Errors.Error: イベント内のエラー
			Errors.Fatal: 未ハンドリングの不特定エラー
		"""
		try:
			return self.__emitter.emit(action, node=node, **event)
		except TypeError as e:
			raise Errors.InvalidSchema(node, event) from e
		except Errors.Error as e:
			if len(e.args) > 0 and not isinstance(e.args[0], Node):
				raise e.__class__(node) from e

			raise e
		except Exception as e:
			raise Errors.Fatal(node, 'Unhandled error') from e

	def __make_event(self, node: Node) -> dict[str, T_Ret | list[T_Ret]]:
		"""ノードの展開プロパティーを元にイベントデータを生成

		Args:
			node: ノード
		Returns:
			イベントデータ
		Raises:
			Errors.Logic: スタックが不足
		"""
		try:
			event: dict[str, T_Ret | list[T_Ret]] = {}
			prop_keys = reversed(node.prop_keys())
			for prop_key in prop_keys:
				if self.__is_prop_list_by(node, prop_key):
					counts = len(getattr(node, prop_key))
					event[prop_key] = list(reversed([self.__stack_pop() for _ in range(counts)]))
				else:
					event[prop_key] = self.__stack_pop()

			return event
		except AssertionError:
			raise Errors.Logic(node, 'Stack is empty')

	def __is_prop_list_by(self, node: Node, prop_key: str) -> bool:
		"""展開プロパティーがリストか判定

		Args:
			node: ノード
			prop_key: プロパティー名
		Returns:
			True = リスト, False = 単体
		"""
		prop_anno = getattr(node.__class__, prop_key).fget.__annotations__['return']
		return hasattr(prop_anno, '__origin__') and prop_anno.__origin__ is list

	def __stack_pop(self) -> T_Ret:
		"""スタックから結果を取得

		Returns:
			結果
		Raises:
			AssertionError: スタックが不足
		"""
		assert self.__stack
		return self.__stack.pop()

	def __put_log_action(self, node: Node, handler_name: str, stacks: tuple[int, int, int], result: T_Ret | None) -> None:
		"""プロセス処理のログを出力

		Args:
			node: ノード
			handler_name: ハンドラー名
			stacks: スタック数(実行前, 実行, 実行後)
			result: 結果
		"""
		if self.__verbose:
			data = self.__make_log_data(node, handler_name, stacks, result)
			joined_data = ', '.join([f'{key}: {value}' for key, value in data.items()])
			indent = ' ' * DSN.elem_counts(node.full_path)
			self.__put_log(f'{indent} {joined_data}')

	def __make_log_data(self, node: Node, handler_name: str, stacks: tuple[int, int, int], result: T_Ret | None) -> dict[str, str]:
		"""プロセス処理のログデータを生成

		Args:
			node: ノード
			handler_name: ハンドラー名
			stacks: スタック数(実行前, 実行, 実行後)
			result: 結果
		Returns:
			ログデータ
		"""
		result_str = str(result).replace('\n', '\\n')
		return {
			str(node): handler_name,
			'stacks': ' -> '.join(map(str, stacks)),
			'result': result_str if len(result_str) < 50 else f'{result_str[:50]}...',
		}

	def __put_log(self, *strs: str) -> None:
		"""ログ出力

		Args:
			*strs: 出力メッセージ
		"""
		if self.__verbose:
			print(*strs)  # FIXME impl Logger
