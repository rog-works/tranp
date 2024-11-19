from collections.abc import Callable
import re
from typing import Any

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.lang.dict import dict_pluck
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.helper.decorator import DecoratorQuery
from rogw.tranp.view.helper.parameter import ParameterHelper
from rogw.tranp.view.render import RendererSetting


def break_last_block(setting: RendererSetting) -> Callable[[str, str], tuple[str, str]]:
	return lambda string, brackets: BlockParser.break_last_block(string, brackets)


def decorator_query(setting: RendererSetting) -> Callable[[list[str]], DecoratorQuery]:
	return lambda decorators: DecoratorQuery.parse(decorators)


def env_get(setting: RendererSetting) -> Callable[[str, Any], Any]:
	return lambda env_path, fallback: dict_pluck(setting.env, env_path, fallback)


def i18n(setting: RendererSetting) -> Callable[[str, str], str]:
	return lambda module_path, local: setting.translator(ModuleDSN.full_joined(setting.translator(alias_dsn(module_path)), local))


def parameter_parse(setting: RendererSetting) -> Callable[[str], ParameterHelper]:
	return lambda parameter: ParameterHelper.parse(parameter)


def reg_fullmatch(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	return lambda pattern, string: re.fullmatch(pattern, string)


def reg_match(setting: RendererSetting) -> Callable[[str, str], re.Match | None]:
	return lambda pattern, string: re.search(pattern, string)


def reg_replace(setting: RendererSetting) -> Callable[[str, str, str], str]:
	return lambda pattern, replace, string: re.sub(pattern, replace, string)


def filter_find(setting: RendererSetting) -> Callable[[str, str], list[str]]:
	return lambda strings, subject: [string for string in strings if string.find(subject) != -1]


def filter_replace(setting: RendererSetting) -> Callable[[list[str], str, str], list[str]]:
	return lambda strings, pattern, replace: [re.sub(pattern, replace, string) for string in strings]


def filter_match(setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
	return lambda strings, pattern: [string for string in strings if re.search(pattern, string)]


def filter_fullmatch(setting: RendererSetting) -> Callable[[list[str], str], list[str]]:
	return lambda strings, pattern: [string for string in strings if re.fullmatch(pattern, string)]
