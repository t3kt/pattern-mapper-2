from dataclasses import dataclass
from typing import List

from common import DataObject, ExtensionBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class ParamState(DataObject):
	name: str
	enable: bool
	bound: bool

	@classmethod
	def fromPar(cls, par: 'Par'):
		return cls(
			name=par.name,
			enable=par.enable,
			bound=par.mode != ParMode.CONSTANT,
		)

@dataclass
class ComponentState(DataObject):
	pass

class ManagedComponent(ExtensionBase):
	def GetParamStates(self) -> List[ParamState]:
		pass
