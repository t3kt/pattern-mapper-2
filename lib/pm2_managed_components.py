from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

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

class SubComponentSpecBuilderInterface(ABC):
	@abstractmethod
	def GetParamStates(self) -> List[ParamState]: pass

	@abstractmethod
	def GetTargetComponent(self) -> Optional['COMP']: pass

	@abstractmethod
	def GetComponentState(self) -> Optional[ComponentState]: pass

class ManagedComponentInterface(ABC):
	@abstractmethod
	def GetManagedComponentState(self) -> ManagedComponentState:
		pass

class ManagedComponent(ExtensionBase):
	def GetParamStates(self) -> List[ParamState]:
		pass
