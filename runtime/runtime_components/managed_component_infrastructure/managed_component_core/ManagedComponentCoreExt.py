from typing import Optional, List, Dict, Any

from common import ExtensionBase
from pm2_managed_components import SubComponentSpecBuilderInterface, ManagedComponentInterface, \
	ManagedComponentState
from pm2_project import PComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ManagedComponentCore(ExtensionBase, ManagedComponentInterface):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.paramMap = {}  # type: Dict[str, Par]
		self.Initialize()

	def Initialize(self):
		self.paramMap.clear()
		rootBuilder = self._RootCompSpecBuilder
		if rootBuilder:
			for par in rootBuilder.GetPars():
				self.paramMap[par.name] = par
		for subBuilder in self._SubCompSpecBuilders:
			name = subBuilder.GetTargetComponentName()
			if not name:
				continue
			prefix = name + ':'
			for par in subBuilder.GetPars():
				self.paramMap[prefix + par.name] = par

	@property
	def _RootCompSpecBuilder(self) -> Optional[SubComponentSpecBuilderInterface]:
		return self.par.Rootcompspec.eval()

	@property
	def _SubCompSpecBuilders(self) -> List[SubComponentSpecBuilderInterface]:
		par = self.par.Subcompspecs  # type: Par
		return par.evalOPs()

	def GetManagedComponentState(self) -> ManagedComponentState:
		rootSpecBuilder = self._RootCompSpecBuilder
		subStates = []
		for subComp in self._SubCompSpecBuilders:
			state = subComp.GetComponentState()
			if state:
				subStates.append(state)
		return ManagedComponentState(
			params=rootSpecBuilder.GetParamStates() if rootSpecBuilder else [],
			subComps=subStates,
		)

	def _GetPar(self, name: str) -> Optional['Par']:
		return self.paramMap.get(name)

	def GetParVal(self, name: str):
		par = self._GetPar(name)
		if par is None:
			self._LogEvent(f'par not found: {name!r}')
			return None
		return par.eval()

	def SetParVal(self, name: str, val):
		par = self._GetPar(name)
		if par is None:
			self._LogEvent(f'par not found: {name!r}')
			return
		if par.mode != ParMode.CONSTANT:
			self._LogEvent(f'par {name!r} mode is not constant: {par.mode}')
			return
		par.val = val

	def GetAllParVals(self) -> Dict[str, Any]:
		return {
			name: par.eval()
			for name, par in self.paramMap.items()
		}

	def GetTypeCode(self) -> str: return self.par.Typecode.eval()

	@property
	def _HostComponent(self) -> 'COMP': return self.par.Hostcomp.eval()

	def GetComponentSpec(self) -> PComponentSpec:
		self.Initialize()
		comp = self._HostComponent
		spec = PComponentSpec(
			compType=self.GetTypeCode(),
			name=comp.name,
		)
		for name, par in self.paramMap.items():
			if par.mode != ParMode.CONSTANT:
				continue
			if ':' in name:
				subName, parName = name.split(':')
				if subName in spec.subCompPars:
					spec.subCompPars[subName][parName] = par.eval()
				else:
					spec.subCompPars[subName] = {parName: par.eval()}
			else:
				spec.pars[name] = par.eval()
		return spec

	def SetComponentSpec(self, spec: PComponentSpec):
		self.Initialize()
		for name, par in self.paramMap.items():
			if par.mode != ParMode.CONSTANT:
				continue
			val = par.default
			if ':' in name:
				subName, parName = name.split(':')
				if subName in spec.subCompPars:
					subPars = spec.subCompPars[subName]
					if parName in subPars:
						val = subPars[parName]
			elif name in spec.pars:
				val = spec.pars[name]
			par.val = val
