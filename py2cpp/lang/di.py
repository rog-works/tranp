from types import FunctionType, MethodType
from typing import Any, Callable, cast

from py2cpp.lang.locator import T_Curried, T_Inst, T_Injector


class DI:
	"""DIコンテナー。シンボルとファクトリー(コンストラクターを含む)をマッピングし、解決時に生成したインスタンスを管理"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__instances: dict[type, Any] = {}
		self.__injectors: dict[type, T_Injector] = {}

	def can_resolve(self, symbol: type) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol (type): シンボル
		Returns:
			bool: True = 解決できる
		"""
		return self.__find_symbol(symbol) is not None

	def register(self, symbol: type[T_Inst], injector: T_Injector) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol (type[T_Inst]): シンボル
			injector (T_Injector): ファクトリー(関数/メソッド/クラス)
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		if self.can_resolve(symbol):
			raise ValueError(f'Already defined. symbol: {symbol}')

		self.__injectors[symbol] = injector

	def unregister(self, symbol: type[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを解除

		Args:
			symbol (type[T_Inst]): シンボル
		"""
		found_symbol = self.__find_symbol(symbol)
		if found_symbol is not None:
			del self.__injectors[found_symbol]

		if found_symbol in self.__instances:
			del self.__instances[found_symbol]

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
			kwargs = self.__inject_kwargs(injector)
			self.__instances[found_symbol] = injector(**kwargs)

		return self.__instances[found_symbol]

	def __find_symbol(self, symbol: type[T_Inst]) -> type[T_Inst] | None:
		"""シンボルを検索

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			type[T_Inst] | None: シンボル
		"""
		return symbol if symbol in self.__injectors else None

	def __inject_kwargs(self, injector: T_Injector) -> dict[str, Any]:
		"""注入する引数リストを生成

		Args:
			injector (T_Injector): ファクトリー(関数/メソッド/クラス)
		Returns:
			dict[str, Any]: 引数リスト
		Raises:
			ValueError: 未登録のシンボルが引数に存在
		"""
		invoker = self.__to_invoker(injector)
		annos = self.__invoke_annotations(invoker)
		return {key: self.resolve(anno) for key, anno in annos.items()}

	def __to_invoker(self, factory: type[T_Inst] | Callable[..., T_Inst]) -> Callable[..., T_Inst]:
		"""呼び出し関数に変換

		Args:
			factory (type[T_Inst] | Callable[..., T_Inst]): ファクトリー(関数/メソッド/クラス)
		Returns:
			Callable[..., T_Inst]: 呼び出し関数
		"""
		if isinstance(factory, (FunctionType, MethodType)):
			return factory
		else:
			return cast(Callable[..., T_Inst], factory.__init__)

	def __invoke_annotations(self, invoker: Callable[..., T_Inst]) -> dict[str, type]:
		"""引数のアノテーションを取得

		Args:
			invoker (Callable[..., T_Inst]): 呼び出し関数
		Returns:
			dict[str, type]: アノテーションリスト
		"""
		annos = getattr(invoker, '__annotations__', {}) if hasattr(invoker, '__annotations__') else {}
		return {key: anno for key, anno in annos.items() if key != 'return'}

	def curry(self, factory: T_Injector, expect: type[T_Curried]) -> T_Curried:
		"""指定のファクトリーをカリー化した関数を返却

		Args:
			factory (T_Injector): ファクトリー(関数/メソッド/クラス)
			expect (type[T_Curried]): 期待するカリー化関数のシグネチャー
		Returns:
			T_Curried: カリー化関数
		"""
		calls = self.__to_invoker(factory)
		annos = self.__invoke_annotations(calls)
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

	def clone(self) -> 'DI':
		"""シンボルのマッピング情報のみコピーした複製を生成

		Returns:
			DI: 複製したインスタンス
		"""
		di = DI()
		for symbol, injector in self.__injectors.items():
			di.register(symbol, injector)

		return di
