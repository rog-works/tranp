from types import FunctionType, MethodType
from typing import Any, Callable, cast

from py2cpp.lang.locator import T_Curried, T_Inst, T_Injector


class DI:
	"""DIコンテナー。シンボルとファクトリー(コンストラクターを含む)をマッピングし、解決時に生成したインスタンスを管理

	Note:
		@see py2cpp.lang.locator.Locator
	"""

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

	def bind(self, symbol: type[T_Inst], injector: T_Injector) -> None:
		"""シンボルとファクトリーのマッピングを登録

		Args:
			symbol (type[T_Inst]): シンボル
			injector (T_Injector): ファクトリー(関数/メソッド/クラス)
		Raises:
			ValueError: 登録済みのシンボルを指定
		"""
		binded_symbol = self.__acceptable_symbol(symbol)
		if self.can_resolve(binded_symbol):
			raise ValueError(f'Already defined. symbol: {symbol}')

		self.__injectors[binded_symbol] = injector

	def unbind(self, symbol: type[T_Inst]) -> None:
		"""シンボルとファクトリーのマッピングを解除

		Args:
			symbol (type[T_Inst]): シンボル
		"""
		found_symbol = self.__find_symbol(symbol)
		if found_symbol is not None:
			del self.__injectors[found_symbol]

		if found_symbol in self.__instances:
			del self.__instances[found_symbol]

	def rebind(self, symbol: type[T_Inst], injector: T_Injector) -> None:
		"""シンボルとファクトリーのマッピングを再登録

		Args:
			symbol (type[T_Inst]): シンボル
			injector (T_Injector): ファクトリー(関数/メソッド/クラス)
		"""
		if self.can_resolve(symbol):
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

	def __acceptable_symbol(self, symbol: type[T_Inst]) -> type[T_Inst]:
		"""受け入れ可能なシンボルに変換

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			type[T_Inst]: シンボル
		Note:
			XXX Generic型は型の解決結果が不明瞭で扱いにくいためオリジナルの型のみ受け入れ
			```python
			# Generic型を登録にした場合(=曖昧な例)
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
		find_symbol = self.__acceptable_symbol(symbol)
		return find_symbol if find_symbol in self.__injectors else None

	def __inject_kwargs(self, injector: T_Injector) -> dict[str, Any]:
		"""注入する引数リストを生成

		Args:
			injector (T_Injector): ファクトリー(関数/メソッド/クラス)
		Returns:
			dict[str, Any]: 引数リスト
		Raises:
			ValueError: 未登録のシンボルが引数に存在
		"""
		annotated = self.__to_annotated(injector)
		annos = self.__pluck_annotations(annotated)
		return {key: self.resolve(anno) for key, anno in annos.items()}

	def __to_annotated(self, factory: type[T_Inst] | Callable[..., T_Inst]) -> Callable[..., T_Inst]:
		"""アノテーション取得用の呼び出し対象の関数に変換

		Args:
			factory (type[T_Inst] | Callable[..., T_Inst]): ファクトリー(関数/メソッド/クラス)
		Returns:
			Callable[..., T_Inst]: 呼び出し対象の関数
		"""
		if isinstance(factory, (FunctionType, MethodType)):
			return factory
		else:
			return cast(Callable[..., T_Inst], factory.__init__)

	def __pluck_annotations(self, annotated: Callable[..., T_Inst]) -> dict[str, type]:
		"""引数のアノテーションを取得

		Args:
			annotated (Callable[..., T_Inst]): 呼び出し対象の関数
		Returns:
			dict[str, type]: 引数のアノテーションリスト
		"""
		annos = getattr(annotated, '__annotations__', {}) if hasattr(annotated, '__annotations__') else {}
		return {key: anno for key, anno in annos.items() if key != 'return'}

	def currying(self, factory: T_Injector, expect: type[T_Curried]) -> T_Curried:
		"""指定のファクトリーをカリー化して返却

		Args:
			factory (T_Injector): ファクトリー(関数/メソッド/クラス)
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

	def invoke(self, factory: type[T_Inst] | Callable[..., T_Inst]) -> T_Inst:
		"""ファクトリーを代替実行し、インスタンスを生成

		Args:
			factory (type[T_Inst] | Callable[..., T_Inst]): ファクトリー(関数/メソッド/クラス)
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
