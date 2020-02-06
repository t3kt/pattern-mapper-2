from typing import Optional, List

from common import ExtensionBase
from pm2_managed_components import SubComponentSpecBuilderInterface, ManagedComponentInterface, \
	ManagedComponentState
from pm2_messaging import Message, MessageHandler

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ManagedComponentCore(ExtensionBase, ManagedComponentInterface, MessageHandler):
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

	def HandleMessage(self, message: Message):
		pass
