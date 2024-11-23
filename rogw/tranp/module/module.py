import hashlib
from typing import override

from rogw.tranp.file.loader import ISourceLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath
import rogw.tranp.syntax.node.definition as defs


class Module:
	"""モジュール。読み込んだモジュールのファイル情報とエントリーポイントを管理"""

	@injectable
	def __init__(self, sources: ISourceLoader, module_path: ModulePath, entrypoint: defs.Entrypoint) -> None:
		"""インスタンスを生成

		Args:
			sources (ISourceLoader): ソースコードローダー @inject
			module_path (ModulePath): モジュールパス
			entrypoint (Entrypoint): エントリーポイント
		"""
		self.__module_path = module_path
		self.__entrypoint = entrypoint
		self.__sources = sources
		self.__identity: str = ''

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.path}>'

	@property
	def module_path(self) -> ModulePath:
		"""ModulePath: モジュールパス"""
		return self.__module_path

	@property
	def path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path.path

	@property
	def entrypoint(self) -> defs.Entrypoint:
		"""Entrypoint: エントリーポイント"""
		return self.__entrypoint

	@property
	def filepath(self) -> str:
		"""str: ファイルパス"""
		return module_path_to_filepath(self.path, f'.{self.module_path.language}')

	def in_storage(self) -> bool:
		"""モジュールのファイルが存在するか判定

		Returns:
			bool: True = 存在
		"""
		return self.__sources.exists(self.filepath)

	def identity(self) -> str:
		"""モジュールの一意な識別子を生成

		Args:
			str: 一意な識別子
		Note:
			### 注意事項
			* このメソッドの一意性は、あくまでもファイルに対してのものである点に注意
			* ファイルが存在しない場合、インスタンスのアドレス値を識別子とし、厳密な一意性は保証しない
		"""
		if not self.__sources.exists(self.filepath):
			return str(id(self))

		if self.__identity:
			return self.__identity

		depends_files = [module_path_to_filepath(import_node.import_path.tokens, f'.{self.module_path.language}') for import_node in self.entrypoint.imports]
		depends_files.append(self.filepath)
		identities = [self.__sources.hash(filepath) for filepath in depends_files]
		self.__identity = hashlib.md5(str(identities).encode('utf-8')).hexdigest()
		return self.__identity
