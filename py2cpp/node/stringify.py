import abc
import re
from typing import Optional

from lark import Token, Tree

from py2cpp.tp_lark.types import Entry


class Stringify:
	def __init__(self, entry: Entry) -> None:
		self.__entry = entry
		self.__commands: list[Command] = []


	def __str__(self) -> str:
		return self.to_string()


	def to_string(self) -> str:
		return self.__stringify()


	def __stringify(self) -> str:
		ctx = Context(self.__entry)
		for command in self.__commands:
			ctx = command.exec(ctx)

		return ctx.string


	def indent(self) -> 'Stringify':
		self.__commands.append(CommandIndent())
		return self


	def flatten(self) -> 'Stringify':
		self.__commands.append(CommandFlatten())
		return self


	def insert(self, index: int, string: str) -> 'Stringify':
		self.__commands.append(CommandInsert(index, string))
		return self


	def join(self, delimiter: str) -> 'Stringify':
		self.__commands.append(CommandJoin(delimiter))
		return self


	def replace(self, pattern: str, replaced: str) -> 'Stringify':
		self.__commands.append(CommandReplace(pattern, replaced))
		return self


class Context:
	def __init__(self, entry: Entry, indent: Optional[str] = None, string: Optional[str] = None, strings: Optional[list[str]] = None) -> None:
		self.__entry = entry
		self.__indent = indent or ''
		self.__string = string or ''
		self.__strings = strings or []


	@property
	def source(self) -> Entry:
		return self.__entry


	@property
	def indent(self) -> str:
		return self.__indent


	@property
	def string(self) -> str:
		return self.__string


	@property
	def strings(self) -> list[str]:
		return self.__strings


class Command:
	@abc.abstractmethod
	def exec(self, ctx: Context) -> Context:
		raise NotImplementedError()


class CommandIndent(Command):
	def exec(self, ctx: Context) -> Context:
		return Context(ctx.source, indent=self.__indent(ctx.source, ctx.indent), strings=ctx.strings)


	def __indent(self, root: Entry, indent: str) -> str:
		if type(root) is Tree:
			for entry in root.iter_subtrees_topdown():
				if type(entry) is Token:
					return entry.value

		return indent


class CommandFlatten(Command):
	def exec(self, ctx: Context) -> Context:
		return Context(ctx.source, strings=self.__flatten(ctx.source))


	def __flatten(self, root: Entry) -> list[str]:
		elems: list[str] = []
		if type(root) is Tree:
			for entry in root.children:
				elems = [*elems, *self.__flatten(entry)]
		elif type(root) is Token:
			elems.append(root.value)
		elif type(root) is str:
			elems.append(root)

		return elems


class CommandInsert(Command):
	def __init__(self, index: int, string: str) -> None:
		self.__index = index
		self.__string = string


	def exec(self, ctx: Context) -> Context:
		return Context(ctx.source, strings=self.__insert(ctx.strings))


	def __insert(self, strings: list[str]) -> list[str]:
		before = strings[:self.__index]
		after = strings[self.__index:]
		return [*before, self.__string, *after]
	

class CommandJoin(Command):
	def __init__(self, delimiter: str) -> None:
		self.__delimiter = delimiter


	def exec(self, ctx: Context) -> Context:
		return Context(ctx.source, string=self.__join(ctx.strings))


	def __join(self, strings: list[str]) -> str:
		return self.__delimiter.join(strings)


class CommandReplace(Command):
	def __init__(self, pattern: str, replaced: str) -> None:
		self.__pattern = pattern
		self.__replaced = replaced


	def exec(self, ctx: Context) -> Context:
		return Context(ctx.source, string=self.__replace(ctx.string))


	def __replace(self, string: str) -> str:
		return re.sub(self.__pattern, self.__replaced, string)
