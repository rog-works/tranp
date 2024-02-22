from types import FunctionType, MethodType
from typing import Any, Callable, TypeAlias, cast

from rogw.tranp.lang.implementation import override
from rogw.tranp.lang.locator import Injector, T_Curried, T_Inst
from rogw.tranp.lang.module import fullyname, load_module_path


class DI:
	"""DIコンテナー。シンボルとファクトリー(コンストラクターを含む)をマッピングし、解決時に生成したインスタンスを管理

	Note:
		@see tranp.lang.locator.Locator
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__instances: dict[type, Any] = {}
		self.__injectors: dict[type, Injector[Any]] = {}

	def can_resolve(self, symbol: type) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol (type): シンボル
		Returns:
			bool: True = 解決できる
		"""
		return self.__inner_binded(symbol)

	def __inner_binded(self, symbol: type) -> bool:
		"""シンボルが登録済みか判定。bindの中のみ直接使用

		Args:
			symbol (type): シンボル
		Returns:
			bool: True = 登録済み
		"""
		return self.__find_symbol(symbol) is not None

	def bind(self, symbol: type[T_Inst], injector: Injector[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol (type[T_Inst]): シンボル
			injector (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
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
			symbol (type[Any]): シンボル
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
			symbol (type[T_Inst]): シンボル
			injector (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
		"""
		if self.__inner_binded(symbol):
			self.unbind(symbol)

		self.bind(symbol, injector)

	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
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
			symbol (type[T_Inst]): シンボル
		Returns:
			type[T_Inst]: シンボル
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
		return getattr(symbol, '__origin__') if hasattr(symbol, '__origin__') else symbol

	def __find_symbol(self, symbol: type[T_Inst]) -> type[T_Inst] | None:
		"""シンボルを検索

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			type[T_Inst] | None: シンボル
		"""
		accept_symbol = self._acceptable_symbol(symbol)
		return accept_symbol if accept_symbol in self.__injectors else None

	def __inject_kwargs(self, injector: Injector[Any]) -> dict[str, Any]:
		"""注入する引数リストを生成

		Args:
			injector (Injector[Any]): ファクトリー(関数/メソッド/クラス)
		Returns:
			dict[str, Any]: 引数リスト
		Raises:
			ValueError: 未登録のシンボルが引数に存在
		"""
		annotated = self.__to_annotated(injector)
		annos = self.__pluck_annotations(annotated)
		return {key: self.resolve(anno) for key, anno in annos.items()}

	def __to_annotated(self, injector: Injector[T_Inst]) -> Callable[..., T_Inst]:
		"""アノテーション取得用の呼び出し対象の関数に変換

		Args:
			injector (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
		Returns:
			Callable[..., T_Inst]: 呼び出し対象の関数
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
			annotated (Callable[..., Any]): 呼び出し対象の関数
		Returns:
			dict[str, type]: 引数のアノテーションリスト
		"""
		annos = getattr(annotated, '__annotations__', {}) if hasattr(annotated, '__annotations__') else {}
		return {key: anno for key, anno in annos.items() if key != 'return'}

	def currying(self, factory: Injector[Any], expect: type[T_Curried]) -> T_Curried:
		"""指定のファクトリーをカリー化して返却

		Args:
			factory (Injector[Any]): ファクトリー(関数/メソッド/クラス)
			expect (type[T_Curried]): カリー化後に期待する関数シグネチャー
		Returns:
			T_Curried: カリー化後の関数
		Note:
			ロケーターが解決可能なシンボルを引数リストの前方から省略していき、
			解決不能なシンボルを残した関数が返却値となる
		"""
		annotated = self.__to_annotated(factory)
		annos = self.__pluck_annotations(annotated)
		curried_args: list[Any] = []
		for anno in annos.values():
			if not self.can_resolve(anno):
				break

			curried_args.append(self.resolve(anno))

		remain_annos = list(annos.values())[len(curried_args):]
		expect_annos = expect.__args__[:-1]  # 引数リスト...戻り値の順なので、末尾の戻り値を除外
		if len(remain_annos) != len(expect_annos):
			raise ValueError(f'Mismatch curring arguments. from: {factory}, expect: {expect}')

		for i, expect_anno in enumerate(expect_annos):
			remain_anno = remain_annos[i]
			if expect_anno is not remain_anno:
				raise ValueError(f'Unexpected remain arguments. from: {factory}, expect: {expect}')

		return cast(T_Curried, lambda *remain_args: factory(*curried_args, *remain_args))

	def invoke(self, factory: Injector[T_Inst]) -> T_Inst:
		"""ファクトリーを代替実行し、インスタンスを生成

		Args:
			factory (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
		Returns:
			T_Inst: 生成したインスタンス
		Note:
			このメソッドを通して生成したインスタンスはキャッシュされず、毎回生成される
		"""
		kwargs = self.__inject_kwargs(factory)
		return factory(**kwargs)

	def clone(self) -> 'DI':
		"""シンボルのマッピング情報のみコピーした複製を生成

		Returns:
			DI: 複製したインスタンス
		"""
		di = DI()
		for symbol, injector in self.__injectors.items():
			di.bind(symbol, injector)

		return di


ModuleDefinitions: TypeAlias = dict[str, str | Injector[Any]]


class LazyDI(DI):
	"""遅延ロードDIコンテナー。マッピングを文字列で管理し、型解決時までモジュールの読み込みを遅延させる"""

	@classmethod
	def instantiate(cls, definitions: ModuleDefinitions) -> 'LazyDI':
		"""インスタンスを生成

		Args:
			definitions (ModuleDefinitions): モジュール定義
		Returns:
			LazyDI: インスタンス
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
			symbol_path (str): シンボル型のパス
			injector (str | Injector[Any]): ファクトリー、またはパス
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		if symbol_path in self.__definitions:
			raise ValueError(f'Already defined. symbol: {symbol_path}')

		self.__definitions[symbol_path] = injector

	def __unregister(self, symbol_path: str) -> None:
		"""マッピングの登録を解除

		Args:
			symbol_path (str): シンボル型のパス
		"""
		if self.__can_resolve(symbol_path):
			del self.__definitions[symbol_path]

	@override
	def can_resolve(self, symbol: type[Any]) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol (type[Any]): シンボル
		Returns:
			bool: True = 解決できる
		"""
		return self.__can_resolve(self.__symbolize(symbol))

	def __can_resolve(self, symbol_path: str) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol_path (str): シンボル型のパス
		Returns:
			bool: True = 解決できる
		"""
		return symbol_path in self.__definitions

	def __symbolize(self, symbol: type[Any]) -> str:
		"""シンボルが解決できるか判定

		Args:
			symbol (type[Any]): シンボル
		Returns:
			str: シンボルパス
		"""
		return fullyname(self._acceptable_symbol(symbol))

	@override
	def bind(self, symbol: type[T_Inst], injector: Injector[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol (type[T_Inst]): シンボル
			injector (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
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
			symbol (type[Any]): シンボル
		"""
		if self.can_resolve(symbol):
			self.__unregister(self.__symbolize(symbol))

		super().unbind(symbol)

	@override
	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
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
			symbol_path (str): シンボル型のパス
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		injector = self.__definitions[symbol_path]
		self.bind(load_module_path(symbol_path), injector if callable(injector) else load_module_path(injector))
