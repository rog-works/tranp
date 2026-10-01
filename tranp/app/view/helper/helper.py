import hashlib
import re
from collections.abc import Callable
from typing import Any

from tranp.app.app.dir import tranp_dir
from tranp.app.dsn.module import ModuleDSN
from tranp.app.dsn.translation import alias_dsn
from tranp.app.lang.dict import dict_pluck
from tranp.app.lang.string import is_quoted_literal as _is_quoted_literal
from tranp.app.view.helper.block import BlockParser
from tranp.app.view.helper.decorator import DecoratorQuery
from tranp.app.view.render import RendererHelperFactory, RendererSetting


class HelperFunctions:
	"""ビューヘルパー(関数)"""

	@classmethod
	def emit_depends(cls, setting: RendererSetting) -> Callable[[str], str]:
		"""Note: @see tranp.app.lang.eventemitter.EventEmitter"""
		return lambda include_path: setting.emitter.emit('depends', path=include_path) or ''

	@classmethod
	def break_last_block(cls, setting: RendererSetting) -> Callable[[str, str], tuple[str, str]]:
		"""Note: @see tranp.app.view.helper.block.BlockParser"""
		return BlockParser.break_last_block

	@classmethod
	def break_separator(cls, setting: RendererSetting) -> Callable[[str, str], list[str]]:
		"""Note: @see tranp.app.view.helper.block.BlockParser"""
		return BlockParser.break_separator

	@classmethod
	def is_quoted_literal(cls, setting: RendererSetting) -> Callable[[str, str], bool]:
		"""Note: @see tranp.app.lang.string.is_quoted_literal"""
		return lambda string, quoted='"': _is_quoted_literal(string, quoted)

	@classmethod
	def parse_decorators(cls, setting: RendererSetting) -> Callable[[list[str]], DecoratorQuery]:
		"""Note: @see tranp.app.view.helper.decorator.DecoratorQuery"""
		return DecoratorQuery.parse

	@classmethod
	def env_get(cls, setting: RendererSetting) -> Callable[[str, Any], Any]:
		"""Note: @see tranp.app.lang.dict.dict_pluck"""
		return lambda env_path, fallback='': dict_pluck(setting.env, env_path, fallback)

	@classmethod
	def tranp_dir(cls, setting: RendererSetting) -> Callable[[], str]:
		"""Note: @see tranp.app.app.dir.tranp_dir"""
		return tranp_dir

	@classmethod
	def i18n(cls, setting: RendererSetting) -> Callable[[str, str], str]:
		"""Note: @see tranp.app.lang.translator.Translator"""
		return lambda module_path, local: setting.translator(ModuleDSN.full_joined(setting.translator(alias_dsn(module_path)), local))

	@classmethod
	def md5(cls, setting: RendererSetting) -> Callable[[str], str]:
		"""Note: @see tranp.app.lang.translator.Translator"""
		return lambda string: hashlib.md5(string.encode('utf-8')).hexdigest()

	@classmethod
	def reg_fullmatch(cls, setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
		"""Note: @see re.fullmatch"""
		return re.fullmatch

	@classmethod
	def reg_match(cls, setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
		"""Note: @see re.search"""
		return re.search

	@classmethod
	def reg_replace(cls, setting: RendererSetting) -> Callable[[str, str, str], str]:
		"""Note: @see re.sub"""
		return re.sub


class HelperFilters:
	"""ビューヘルパー(フィルター)"""

	@classmethod
	def filter_find(cls, setting: RendererSetting) -> Callable[[str, str], list[str]]:
		"""Note: @see str.find"""
		return lambda strings, subject: [string for string in strings if string.find(subject) != -1]

	@classmethod
	def filter_replace(cls, setting: RendererSetting) -> Callable[[list[str], str, str], list[str]]:
		"""Note: @see str.sub"""
		return lambda strings, pattern, replace: [re.sub(pattern, replace, string) for string in strings]

	@classmethod
	def filter_match(cls, setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
		"""Note: @see re.pattern"""
		return lambda strings, pattern: [string for string in strings if re.search(pattern, string)]

	@classmethod
	def filter_fullmatch(cls, setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
		"""Note: @see re.fullmatch"""
		return lambda strings, pattern: [string for string in strings if re.fullmatch(pattern, string)]


def factories() -> tuple[list[RendererHelperFactory], list[RendererHelperFactory]]:
	"""Returns: (ヘルパー一覧, フィルター一覧)"""
	return (
		 [
			HelperFunctions.emit_depends,
			HelperFunctions.break_last_block,
			HelperFunctions.break_separator,
			HelperFunctions.is_quoted_literal,
			HelperFunctions.parse_decorators,
			HelperFunctions.env_get,
			HelperFunctions.tranp_dir,
			HelperFunctions.i18n,
			HelperFunctions.md5,
			HelperFunctions.reg_fullmatch,
			HelperFunctions.reg_match,
			HelperFunctions.reg_replace,
		],
		[
			HelperFilters.filter_find,
			HelperFilters.filter_replace,
			HelperFilters.filter_match,
			HelperFilters.filter_fullmatch,
		],
	)
