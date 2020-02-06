from dataclasses import dataclass, field
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
	name: str
	params: List[ParamState] = field(default_factory=list)

@dataclass
class ManagedComponentState(DataObject):
	params: List[ParamState] = field(default_factory=list)
	subComps: List[ComponentState] = field(default_factory=list)

class ManagedComponent(ExtensionBase):
	def GetParamStates(self) -> List[ParamState]:
		pass
