from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from common import DataObject
from pm2_project import PComponentSpec

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
	def GetPars(self) -> List['Par']: pass

	@abstractmethod
	def GetTargetComponent(self) -> Optional['COMP']: pass

	@abstractmethod
	def GetTargetComponentName(self) -> Optional[str]: pass

	@abstractmethod
	def GetComponentState(self) -> Optional[ComponentState]: pass

class ManagedComponentInterface(ABC):
	@abstractmethod
	def GetManagedComponentState(self) -> ManagedComponentState: pass

	@abstractmethod
	def GetParVal(self, name: str): pass

	@abstractmethod
	def GetAllParVals(self) -> Dict[str, Any]: pass

	@abstractmethod
	def SetParVal(self, name: str, val): pass

	@abstractmethod
	def GetTypeCode(self) -> str: pass

	@abstractmethod
	def GetComponentSpec(self) -> PComponentSpec: pass

	@abstractmethod
	def SetComponentSpec(self, spec: PComponentSpec): pass

class ManagedComponentEditorInterface(ABC):
	@abstractmethod
	def InitializeEditor(self, spec: PComponentSpec): pass

	@abstractmethod
	def SetParVal(self, name: str, val): pass
