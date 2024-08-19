from typing import Callable

from rogw.tranp.errors import FatalError
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.annotation import deprecated, implements
from rogw.tranp.lang.eventemitter import IObservable
from rogw.tranp.semantics.plugin import IPlugin
from rogw.tranp.semantics.reflection.interface import IReflection
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


@deprecated
class CppPlugin(IPlugin):
	"""C++用プラグイン

	Note:
		単項・2項演算をインターセプトし、アドレス変数を実体へ置き換える
		# 変換例
		'Class[CP]' -> 'Class'
		'Class[CSP]' -> 'Class'
		@deprecated 未使用のため削除を検討
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__reflections: Reflections | None = None

	@property
	def reflections(self) -> Reflections:
		"""Symbols: シンボルリゾルバー"""
		if self.__reflections is not None:
			return self.__reflections

		raise FatalError('Symbols is null')

	@implements
	def register(self, observer: IObservable) -> None:
		"""オブザーバーにプラグインを登録

		Args:
			observer (IObserver): オブザーバー
		"""
		if not isinstance(observer, Reflections):
			raise FatalError('Diffrerent observer.')

		self.__reflections = observer

		for key, handler in self.__interceptors().items():
			action = f'on_enter_{key.split('on_')[1]}'
			observer.on(action, handler)

	@implements
	def unregister(self, observer: IObservable) -> None:
		"""オブザーバーからプラグインを解除

		Args:
			observer (IObserver): オブザーバー
		"""
		if self.__reflections != observer:
			raise FatalError('Diffrerent observer.')

		for key, handler in self.__interceptors.items():
			action = f'on_enter_{key.split('on_')[1]}'
			observer.off(action, handler)

		self.__reflections = None

	def __interceptors(self) -> dict[str, Callable[..., IReflection]]:
		"""インターセプトハンドラーの一覧を取得

		Returns:
			dict[str, Callable[..., IReflection]]: ハンドラー一覧
		"""
		return {}

	def on_factor(self, node: defs.Factor, operator: IReflection, value: IReflection) -> list[IReflection]:
		return [operator, self.unpack_cvar_raw(value)]

	def on_not_compare(self, node: defs.NotCompare, operator: IReflection, value: IReflection) -> list[IReflection]:
		return [operator, self.unpack_cvar_raw(value)]

	def on_or_compare(self, node: defs.OrCompare, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_and_compare(self, node: defs.AndCompare, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_comparison(self, node: defs.Comparison, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_or_bitwise(self, node: defs.OrBitwise, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_xor_bitwise(self, node: defs.XorBitwise, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_and_bitwise(self, node: defs.AndBitwise, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_sum(self, node: defs.Sum, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def on_term(self, node: defs.Term, elements: list[IReflection]) -> list[IReflection]:
		return self.each_on_binary_operator(node, elements)

	def each_on_binary_operator(self, node: defs.BinaryOperator, elements: list[IReflection]) -> list[IReflection]:
		first = self.unpack_cvar_raw(elements[0])
		unpacked_elements = [first]
		for index in range(int((len(elements) - 1) / 2)):
			operator = elements[index * 2 + 1]
			right = self.unpack_cvar_raw(elements[index * 2 + 2])
			unpacked_elements.extend([operator, right])

		return unpacked_elements

	def unpack_cvar_raw(self, value_raw: IReflection) -> IReflection:
		"""C++変数型を考慮し、シンボルの実体型を取得。実体型かnullはそのまま返却

		Args:
			value_raw (IReflection): 値のシンボル
		Returns:
			IReflection: シンボル
		"""
		key = CVars.key_from(self.reflections, value_raw)
		if CVars.is_raw_raw(key) or self.reflections.is_a(value_raw, None):
			return value_raw

		# 実体の型を取得出来るまで参照元を辿る
		for origin in value_raw.stacktrace():
			if CVars.is_raw_raw(CVars.key_from(self.reflections, origin)):
				return origin

		raise FatalError(f'Unexpected symbol schema. value: {value_raw}')
