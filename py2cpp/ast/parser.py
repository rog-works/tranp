from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from py2cpp.ast.entry import Entry


@dataclass
class GrammarSettings:
	grammar: str
	start: str = 'file_input'
	algorihtem: str = 'lalr'


class SyntaxParser(metaclass=ABCMeta):
	@abstractmethod
	def parse(self, module_path: str) -> Entry:
		raise NotImplementedError()
