from collections.abc import Callable
import re
from typing import Any

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.lang.dict import dict_pluck
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.helper.decorator import DecoratorQuery
from rogw.tranp.view.helper.parameter import ParameterHelper
from rogw.tranp.view.render import RendererHelperFactory, RendererSetting


def break_last_block(setting: RendererSetting) -> Callable[[str, str], tuple[str, str]]:
	"""Note: @see rogw.tranp.view.helper.block.BlockParser"""
	return lambda string, brackets: BlockParser.break_last_block(string, brackets)


def decorator_query(setting: RendererSetting) -> Callable[[list[str]], DecoratorQuery]:
	"""Note: @see rogw.tranp.view.helper.decorator.DecoratorQuery"""
	return lambda decorators: DecoratorQuery.parse(decorators)


def env_get(setting: RendererSetting) -> Callable[[str, Any], Any]:
	"""Note: @see rogw.tranp.lang.dict.dict_pluck"""
	return lambda env_path, fallback: dict_pluck(setting.env, env_path, fallback)


def i18n(setting: RendererSetting) -> Callable[[str, str], str]:
	"""Note: @see rogw.tranp.lang.translator.Translator"""
	return lambda module_path, local: setting.translator(ModuleDSN.full_joined(setting.translator(alias_dsn(module_path)), local))


def reg_fullmatch(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	"""Note: @see re.fullmatch"""
	return lambda pattern, string: re.fullmatch(pattern, string)


def reg_match(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	"""Note: @see re.search"""
	return lambda pattern, string: re.search(pattern, string)


def reg_replace(setting: RendererSetting) -> Callable[[str, str, str], str]:
	"""Note: @see re.sub"""
	return lambda pattern, replace, string: re.sub(pattern, replace, string)


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
	"""Returns: tuple[list[RendererHelperFactory], list[RendererHelperFactory]]: (ヘルパー一覧, フィルター一覧)"""
	return (
		 [
			break_last_block,
			decorator_query,
			env_get,
			i18n,
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


def parameter_parse(setting: RendererSetting) -> Callable[[str], ParameterHelper]:
	"""Note: @see rogw.tranp.view.helper.parameter.ParameterHelper"""
	return lambda parameter: ParameterHelper.parse(parameter)


def factories_for_cpp() -> tuple[list[RendererHelperFactory], list[RendererHelperFactory]]:
	"""Returns: tuple[list[RendererHelperFactory], list[RendererHelperFactory]]: (ヘルパー一覧, フィルター一覧) ※C++用"""
	return ([parameter_parse], [])
