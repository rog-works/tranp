from collections.abc import Callable
from typing import TypeVar

from rogw.tranp.lang.annotation import deprecated
from rogw.tranp.lang.typehint import ClassTypehint

T = TypeVar('T')


@deprecated
def validation(klass: type[T], lookup_private: bool = True, factory: Callable[[], T] | None = None) -> bool:
	"""クラスの実装スキーマバリデーション

	Args:
		klass: 検証クラス
		lookup_private: プライベートプロパティー抽出フラグ (default = True)
		factory: インスタンスファクトリー (default = None)
	Returns:
		True = 成功
	Raises:
		TypeError: 設計と実体の不一致
	Note:
		@deprecated 設計と実体に食い違いが出ない実装方法が取れるようになったため非推奨
	"""
	hint = ClassTypehint(klass)
	instance = factory() if factory else klass()
	hint_keys = hint.self_vars(lookup_private).keys()
	inst_keys = instance.__dict__.keys()
	exists_from_hint = [key for key in hint_keys if key in inst_keys]
	exists_from_inst = [key for key in inst_keys if key in hint_keys]
	if len(exists_from_hint) != len(exists_from_inst):
		raise TypeError(f'Schema not match. class: {klass.__name__}, expected self attributes: ({",".join(hint_keys)})')

	return True
