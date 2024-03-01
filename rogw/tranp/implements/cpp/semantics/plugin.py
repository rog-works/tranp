from typing import Callable, cast

from rogw.tranp.errors import FatalError
from rogw.tranp.implements.cpp.semantics.cvars import CVars
from rogw.tranp.lang.eventemitter import IObservable
from rogw.tranp.lang.implementation import deprecated, implements
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.plugin import IPlugin
from rogw.tranp.semantics.symbol import Reflection
from rogw.tranp.semantics.symbols import Symbols


@deprecated
class CppPlugin(IPlugin):
	"""C++用プラグイン

	Note:
		単項・2項演算をインターセプトし、アドレス変数を実体へ置き換える
		# 変換例
		'Class[CP]' -> 'Class'
		'Class[CSP]' -> 'Class'
		@deprecated 実質未使用のため削除を検討
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__symbols: Symbols | None = None

	@property
	def symbols(self) -> Symbols:
		"""Symbols: シンボルリゾルバー"""
		if self.__symbols is not None:
			return self.__symbols

		raise FatalError('Symbols is null')

	@implements
	def register(self, observer: IObservable) -> None:
		"""オブザーバーにプラグインを登録

		Args:
			observer (IObserver): オブザーバー
		"""
		self.__symbols = cast(Symbols, observer)

		for key, handler in self.__interceptors().items():
			action = f'on_enter_{key.split('on_')[1]}'
			self.symbols.on(action, handler)

	@implements
	def unregister(self, observer: IObservable) -> None:
		"""オブザーバーからプラグインを解除

		Args:
			observer (IObserver): オブザーバー
		"""
		if self.__symbols != observer:
			raise FatalError('Diffrerent observer.')

		for key, handler in self.__interceptors.items():
			action = f'on_enter_{key.split('on_')[1]}'
			self.symbols.off(action, handler)

		self.__symbols = None

	def __interceptors(self) -> dict[str, Callable[..., Reflection]]:
		"""インターセプトハンドラーの一覧を取得

		Returns:
			dict[str, Callable[..., SymbolRaw]]: ハンドラー一覧
		"""
		return {}

	def on_factor(self, node: defs.Factor, operator: Reflection, value: Reflection) -> list[Reflection]:
		return [operator, self.unpack_cvar_raw(value)]

	def on_not_compare(self, node: defs.NotCompare, operator: Reflection, value: Reflection) -> list[Reflection]:
		return [operator, self.unpack_cvar_raw(value)]

	def on_or_compare(self, node: defs.OrCompare, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_and_compare(self, node: defs.AndCompare, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_comparison(self, node: defs.Comparison, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_or_bitwise(self, node: defs.OrBitwise, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_xor_bitwise(self, node: defs.XorBitwise, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_and_bitwise(self, node: defs.AndBitwise, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_shift_bitwise(self, node: defs.ShiftBitwise, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_sum(self, node: defs.Sum, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def on_term(self, node: defs.Term, elements: list[Reflection]) -> list[Reflection]:
		return self.each_on_binary_operator(node, elements)

	def each_on_binary_operator(self, node: defs.BinaryOperator, elements: list[Reflection]) -> list[Reflection]:
		first = self.unpack_cvar_raw(elements[0])
		unpacked_elements = [first]
		for index in range(int((len(elements) - 1) / 2)):
			operator = elements[index * 2 + 1]
			right = self.unpack_cvar_raw(elements[index * 2 + 2])
			unpacked_elements.extend([operator, right])

		return unpacked_elements

	def unpack_cvar_raw(self, value_raw: Reflection) -> Reflection:
		"""C++変数型を考慮し、シンボルの実体型を取得。実体型かnullはそのまま返却

		Args:
			value_raw (SymbolRaw): 値のシンボル
		Returns:
			SymbolRaw: シンボル
		"""
		key = CVars.key_from(self.symbols, value_raw)
		if CVars.is_raw_raw(key) or self.symbols.is_a(value_raw, None):
			return value_raw

		# 実体の型を取得出来るまで参照元を辿る
		for origin in value_raw.hierarchy():
			if CVars.is_raw_raw(CVars.key_from(self.symbols, origin)):
				return origin

		raise FatalError(f'Unexpected symbol schema. value: {value_raw}')
