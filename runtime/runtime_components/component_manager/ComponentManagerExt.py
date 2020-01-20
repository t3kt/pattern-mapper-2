from typing import List

from common import createFromTemplate, OPAttrs, loggedmethod, simpleloggedmethod
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentManager(RuntimeComponent):
	@property
	def _Components(self) -> List['SerializableComponentOrCOMP']:
		return self.ops('contents/comp__*')

	@property
	def _ComponentsInOrder(self):
		return list(sorted(self._Components, key=lambda c: c.nodeY))

	@property
	def _IsChain(self):
		return self.par.Compstructure == 'chain'

	def WriteComponentSpecs(self) -> List[PComponentSpec]:
		comps = self._ComponentsInOrder
		return [
			comp.GetComponentSpec()
			for comp in comps
		]

	def ReadComponentSpecs(self, specs: List[PComponentSpec]):
		self.ClearComponents()
		for spec in specs:
			self.AddComponent(spec)

	def ClearComponents(self):
		for comp in self._Components:
			comp.destroy()

	def AddComponent(self, spec: PComponentSpec):
		pass
