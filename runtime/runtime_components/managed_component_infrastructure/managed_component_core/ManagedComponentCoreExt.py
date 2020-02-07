from typing import Optional, List, Dict, Any

from common import ExtensionBase
from pm2_managed_components import SubComponentSpecBuilderInterface, ManagedComponentInterface, \
	ManagedComponentState

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
