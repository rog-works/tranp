import hashlib
import re
from collections.abc import Callable
from typing import Any

from tranp.app.dsn.module import ModuleDSN
from tranp.app.dsn.translation import alias_dsn
from tranp.app.lang.dict import dict_pluck
from tranp.app.lang.string import is_quoted_literal as _is_quoted_literal
from tranp.app.view.helper.block import BlockParser
from tranp.app.view.helper.decorator import DecoratorQuery
from tranp.app.view.render import RendererHelperFactory, RendererSetting


def emit_depends(setting: RendererSetting) -> Callable[[str], str]:
	"""Note: @see tranp.app.lang.eventemitter.EventEmitter"""
	return lambda include_path: setting.emitter.emit('depends', path=include_path) or ''


def break_last_block(setting: RendererSetting) -> Callable[[str, str], tuple[str, str]]:
	"""Note: @see tranp.app.view.helper.block.BlockParser"""
	return BlockParser.break_last_block


def break_separator(setting: RendererSetting) -> Callable[[str, str], list[str]]:
	"""Note: @see tranp.app.view.helper.block.BlockParser"""
	return BlockParser.break_separator


def is_quoted_literal(setting: RendererSetting) -> Callable[[str, str], bool]:
	"""Note: @see tranp.app.lang.string.is_quoted_literal"""
	return lambda string, quoted='"': _is_quoted_literal(string, quoted)


def parse_decorators(setting: RendererSetting) -> Callable[[list[str]], DecoratorQuery]:
	"""Note: @see tranp.app.view.helper.decorator.DecoratorQuery"""
	return DecoratorQuery.parse


def env_get(setting: RendererSetting) -> Callable[[str, Any], Any]:
	"""Note: @see tranp.app.lang.dict.dict_pluck"""
	return lambda env_path, fallback='': dict_pluck(setting.env, env_path, fallback)


def i18n(setting: RendererSetting) -> Callable[[str, str], str]:
	"""Note: @see tranp.app.lang.translator.Translator"""
	return lambda module_path, local: setting.translator(ModuleDSN.full_joined(setting.translator(alias_dsn(module_path)), local))


def md5(setting: RendererSetting) -> Callable[[str], str]:
	"""Note: @see tranp.app.lang.translator.Translator"""
	return lambda string: hashlib.md5(string.encode('utf-8')).hexdigest()


def reg_fullmatch(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	"""Note: @see re.fullmatch"""
	return re.fullmatch


def reg_match(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	"""Note: @see re.search"""
	return re.search


def reg_replace(setting: RendererSetting) -> Callable[[str, str, str], str]:
	"""Note: @see re.sub"""
	return re.sub


def filter_find(setting: RendererSetting) -> Callable[[str, str], list[str]]:
	"""Note: @see str.find"""
	return lambda strings, subject: [string for string in strings if string.find(subject) != -1]


def filter_replace(setting: RendererSetting) -> Callable[[list[str], str, str], list[str]]:
	"""Note: @see str.sub"""
	return lambda strings, pattern, replace: [re.sub(pattern, replace, string) for string in strings]


def filter_match(setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
	"""Note: @see re.pattern"""
	return lambda strings, pattern: [string for string in strings if re.search(pattern, string)]


def filter_fullmatch(setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
	"""Note: @see re.fullmatch"""
	return lambda strings, pattern: [string for string in strings if re.fullmatch(pattern, string)]


def factories() -> tuple[list[RendererHelperFactory], list[RendererHelperFactory]]:
	"""Returns: (ヘルパー一覧, フィルター一覧)"""
	return (
		 [
			emit_depends,
			break_last_block,
			break_separator,
			is_quoted_literal,
			parse_decorators,
			env_get,
			i18n,
			md5,
			reg_fullmatch,
			reg_match,
			reg_replace,
		],
		[
			filter_find,
			filter_replace,
			filter_match,
			filter_fullmatch,
		],
	)
