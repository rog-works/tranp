import glob
import os
import re

from rogw.tranp.errors import LogicError
from rogw.tranp.module.types import ModulePath, ModulePaths


def include_module_paths(input_glob: str, exclude_patterns: list[str]) -> ModulePaths:
	"""指定のマッチングパターンに一致するモジュールのパスリストを抽出

	Args:
		input_glob (str): 入力パターン(Glob)
		exclude_patterns (list[str]): 除外パターンリスト(正規表現)
	Returns:
		ModulePaths: モジュールパスリスト
	Raises:
		LogicError: 対象が存在しない
	"""
	candidate_filepaths = glob.glob(input_glob, recursive=True)
	exclude_exps = [re.compile(rf'{exclude.replace("*", '.*')}') for exclude in exclude_patterns]
	module_paths = ModulePaths()
	for filepath in candidate_filepaths:
		excluded = len([True for exclude_exp in exclude_exps if exclude_exp.fullmatch(filepath)]) > 0
		if not excluded:
			basepath, extention = os.path.splitext(filepath)
			module_paths.append(ModulePath(basepath.replace(os.path.sep, '.'), language=extention[1:]))

	if len(module_paths) == 0:
		raise LogicError(f'No target found. input_dir: {input_glob}, excludes: {exclude_patterns}')

	return module_paths
