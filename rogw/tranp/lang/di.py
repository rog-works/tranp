from collections.abc import Callable
from types import FunctionType, MethodType
from typing import Any, Self, TypeAlias, cast, override

from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.locator import Injector, Locator, T_Inst
from rogw.tranp.lang.module import to_fullyname, load_module_path

ModuleDefinitions: TypeAlias = dict[str, str | Injector[Any]]


class DI:
	"""DIコンテナー。シンボルとファクトリー(コンストラクターを含む)をマッピングし、解決時に生成したインスタンスを管理"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__instances: dict[type, Any] = {}
		self.__injectors: dict[type, Injector[Any]] = {}
		self.__invocations: dict[str, dict[str, type]] = {}

	@duck_typed(Locator)
	def can_resolve(self, symbol: type) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol: シンボル
		Returns:
			True = 解決できる
		"""
		return self.__inner_binded(symbol)

	def __inner_binded(self, symbol: type) -> bool:
		"""シンボルが登録済みか判定。bindの中のみ直接使用

		Args:
			symbol: シンボル
		Returns:
			True = 登録済み
		"""
		return self.__find_symbol(symbol) is not None

	def bind(self, symbol: type[T_Inst], injector: Injector[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol: シンボル
			injector: ファクトリー(関数/メソッド/クラス)
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		accept_symbol = self._acceptable_symbol(symbol)
		if self.__inner_binded(accept_symbol):
			raise ValueError(f'Already defined. symbol: {symbol}')

		self.__injectors[accept_symbol] = injector

	def unbind(self, symbol: type[Any]) -> None:
		"""シンボルとファクトリーのマッピングを解除

		Args:
			symbol: シンボル
		"""
		found_symbol = self.__find_symbol(symbol)
		if found_symbol is not None:
			if found_symbol in self.__injectors:
				del self.__injectors[found_symbol]

			if found_symbol in self.__instances:
				del self.__instances[found_symbol]

	def rebind(self, symbol: type[T_Inst], injector: Injector[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを再登録

		Args:
			symbol: シンボル
			injector: ファクトリー(関数/メソッド/クラス)
		"""
		if self.__inner_binded(symbol):
			self.unbind(symbol)

		self.bind(symbol, injector)

	@duck_typed(Locator)
	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol: シンボル
		Returns:
			インスタンス
		Raises:
			ValueError: 未登録のシンボルを指定
		"""
		found_symbol = self.__find_symbol(symbol)
		if found_symbol is None:
			raise ValueError(f'Unresolve symbol. symbol: {symbol}')

		if found_symbol not in self.__instances:
			injector = self.__injectors[found_symbol]
			self.__instances[found_symbol] = self.invoke(injector)

		return self.__instances[found_symbol]

	def _acceptable_symbol(self, symbol: type[T_Inst]) -> type[T_Inst]:
		"""受け入れ可能なシンボルに変換

		Args:
			symbol: シンボル
		Returns:
			シンボル
		Note:
			XXX Generic型は型の解決結果が不明瞭で扱いにくいため、オリジナルの型のみ受け入れ
			```python
			# Generic型で登録した場合(=曖昧な例)
			di.bind(Gen[A], lambda: Gen[B]())
			di.resolve(Gen[A])  # OK
			di.resolve(Gen[B])  # NG
			di.resolve(Gen['A'])  # NG
			di.resolve(Gen)  # NG

			# オリジナルの型で登録した場合
			di.bind(Gen[A], lambda: Gen[B])
			di.resolve(Gen[A])  # OK
			di.resolve(Gen[B])  # OK
			di.resolve(Gen['A'])  # OK
			di.resolve(Gen)  # OK
			```
		"""
		return getattr(symbol, '__origin__', symbol)

	def __find_symbol(self, symbol: type[T_Inst]) -> type[T_Inst] | None:
		"""シンボルを検索

		Args:
			symbol: シンボル
		Returns:
			シンボル
		"""
		accept_symbol = self._acceptable_symbol(symbol)
		return accept_symbol if accept_symbol in self.__injectors else None

	@duck_typed(Locator)
	def invoke(self, factory: Injector[T_Inst], *remain_args: Any) -> T_Inst:
		"""ファクトリーを代替実行し、インスタンスを生成

		Args:
			factory: ファクトリー(関数/メソッド/クラス)
			*remain_args: 残りの位置引数
		Returns:
			生成したインスタンス
		Note:
			```
			* ロケーターが解決可能なシンボルをファクトリーの引数リストの前方から省略していき、解決不能な引数を残りの位置引数として受け取る
			* このメソッドを通して生成したインスタンスはキャッシュされず、毎回生成される
			```
		"""
		fullyname = to_fullyname(factory)
		found = fullyname in self.__invocations
		if not found:
			annotated = self.__to_annotated(factory)
			self.__invocations[fullyname] = self.__pluck_annotations(annotated)

		annos = self.__invocations[fullyname]
		curried_args: list[type] = []
		for anno in annos.values():
			if not self.can_resolve(anno):
				break

			curried_args.append(self.resolve(anno))

		if not found:
			self.__assert_invoke(factory, annos, curried_args, *remain_args)

		return factory(*curried_args, *remain_args)

	def __to_annotated(self, injector: Injector[T_Inst]) -> Callable[..., T_Inst]:
		"""アノテーション取得用の呼び出し対象の関数に変換

		Args:
			injector: ファクトリー(関数/メソッド/クラス)
		Returns:
			呼び出し対象の関数
		"""
		if isinstance(injector, (FunctionType, MethodType)):
			return injector
		elif not isinstance(injector, type) and hasattr(injector, '__call__'):
			return injector.__call__
		else:
			return cast(Callable[..., T_Inst], injector.__init__)

	def __pluck_annotations(self, annotated: Callable[..., Any]) -> dict[str, type]:
		"""引数のアノテーションを取得

		Args:
			annotated: 呼び出し対象の関数
		Returns:
			引数のアノテーションリスト
		"""
		annos = getattr(annotated, '__annotations__', {})
		return {key: anno for key, anno in annos.items() if key != 'return'}

	def __assert_invoke(self, injector: Injector, annos: dict[str, type], curried_args: list[type], *remain_args: Any) -> None:
		"""代替呼び出しのバリデーション

		Args:
			injector: ファクトリー(関数/メソッド/クラス)
			annos: 引数のアノテーションリスト
			curried_args: カリー化対象の位置引数
			*remain_args: 余りの位置引数
		Raises:
			ValueError: 呼び出しシグネチャーが不正
		"""
		# XXX ジェネリック型の場合isinstanceで比較できないため、オリジナルの型を期待値として抽出
		expect_types = [getattr(expect, '__origin__', expect) for expect in list(annos.values())[len(curried_args):]]
		allow_types = [type(arg) for index, arg in enumerate(remain_args) if isinstance(arg, expect_types[index])]
		if len(expect_types) != len(allow_types):
			raise ValueError(f'Mismatch invoke arguments. factory: {injector}, expect: {expect_types}, actual: {[type(arg) for arg in remain_args]}')

	def _clone(self) -> Self:
		"""インスタンスを複製

		Returns:
			複製したインスタンス
		"""
		di = self.__class__()
		di.__instances = self.__instances.copy()
		di.__injectors = self.__injectors.copy()
		return di

	def combine(self, other: Self) -> Self:
		"""マージ対象と合成した新たなインスタンスを生成

		Args:
			other: マージ対象のインスタンス
		Returns:
			合成したインスタンス
		Raises:
			TypeError: マージ対象が自身と相違した派生クラス
		Note:
			```
			* 戻り値の型はレシーバーのインスタンスに倣う
			* 同じシンボルはマージ対象のインスタンスで上書きされる
			```
		"""
		if not isinstance(self, other.__class__):
			raise TypeError(f'Merging not allowed. not related. self: {self.__class__}, other: {other.__class__}')

		di = self._clone()
		di.__instances = {**di.__instances, **other.__instances}
		di.__injectors = {**di.__injectors, **other.__injectors}
		return di


class LazyDI(DI):
	"""遅延ロードDIコンテナー。マッピングを文字列で管理し、型解決時までモジュールの読み込みを遅延させる"""

	@classmethod
	def instantiate(cls, definitions: ModuleDefinitions) -> Self:
		"""インスタンスを生成

		Args:
			definitions: モジュール定義
		Returns:
			インスタンス
		"""
		di = cls()
		for symbol_path, injector in definitions.items():
			di.__register(symbol_path, injector)

		return di

	def __init__(self) -> None:
		"""インスタンスを生成"""
		super().__init__()
		self.__definitions: ModuleDefinitions = {}

	def __register(self, symbol_path: str, injector: str | Injector[Any]) -> None:
		"""マッピングの登録を追加

		Args:
			symbol_path: シンボル型のパス
			injector: ファクトリー、またはパス
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		if symbol_path in self.__definitions:
			raise ValueError(f'Already defined. symbol: {symbol_path}')

		self.__definitions[symbol_path] = injector

	def __unregister(self, symbol_path: str) -> None:
		"""マッピングの登録を解除

		Args:
			symbol_path: シンボル型のパス
		"""
		if self.__can_resolve(symbol_path):
			del self.__definitions[symbol_path]

	@override
	def can_resolve(self, symbol: type[Any]) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol: シンボル
		Returns:
			True = 解決できる
		"""
		return self.__can_resolve(self.__symbolize(symbol))

	def __can_resolve(self, symbol_path: str) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol_path: シンボル型のパス
		Returns:
			True = 解決できる
		"""
		return symbol_path in self.__definitions

	def __symbolize(self, symbol: type[Any]) -> str:
		"""シンボルが解決できるか判定

		Args:
			symbol: シンボル
		Returns:
			シンボルパス
		"""
		return to_fullyname(self._acceptable_symbol(symbol))

	@override
	def bind(self, symbol: type[T_Inst], injector: Injector[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol: シンボル
			injector: ファクトリー(関数/メソッド/クラス)
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		symbol_path = self.__symbolize(symbol)
		if not self.__can_resolve(symbol_path):
			self.__register(symbol_path, injector)

		return super().bind(symbol, injector)

	@override
	def unbind(self, symbol: type[Any]) -> None:
		"""シンボルとファクトリーのマッピングを解除

		Args:
			symbol: シンボル
		"""
		if self.can_resolve(symbol):
			self.__unregister(self.__symbolize(symbol))

		super().unbind(symbol)

	@override
	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol: シンボル
		Returns:
			インスタンス
		Raises:
			ValueError: 未登録のシンボルを指定
		"""
		symbol_path = self.__symbolize(symbol)
		if not super().can_resolve(symbol) and self.__can_resolve(symbol_path):
			self.__bind_proxy(symbol_path)

		return super().resolve(symbol)

	def __bind_proxy(self, symbol_path: str) -> None:
		"""シンボルとファクトリーのマッピングを代替登録

		Args:
			symbol_path: シンボル型のパス
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		injector = self.__definitions[symbol_path]
		self.bind(load_module_path(symbol_path), injector if callable(injector) else load_module_path(injector))

	@override
	def _clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			複製したインスタンス
		"""
		di = super()._clone()
		di.__definitions = self.__definitions.copy()
		return di

	@override
	def combine(self, other: Self) -> Self:
		"""マージ対象と合成した新たなインスタンスを生成

		Args:
			other: マージ対象のインスタンス
		Returns:
			合成したインスタンス
		Raises:
			TypeError: マージ対象が自身と相違した派生クラス
		Note:
			```
			* 戻り値の型はレシーバーのインスタンスに倣う
			* 同じシンボルはマージ対象のインスタンスで上書きされる
			```
		"""
		di = super().combine(other)
		di.__definitions = {**self.__definitions, **other.__definitions}
		return di
