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

	@loggedmethod
	def WriteComponentSpecs(self) -> List[PComponentSpec]:
		comps = self._ComponentsInOrder
		return [
			comp.GetComponentSpec()
			for comp in comps
		]

	@loggedmethod
	def ReadComponentSpecs(self, specs: List[PComponentSpec]):
		self.ClearComponents()
		for spec in specs:
			self.AddComponent(spec)

	@loggedmethod
	def ClearComponents(self):
		for comp in self._Components:
			comp.destroy()
		if self._IsChain:
			self.op('contents/__sel_chop_out').par.chop = self.op('contents/__chop_in')

	@loggedmethod
	def AddComponent(self, spec: PComponentSpec):
		templatePath = self.op('type_table')[spec.compType, 'template']
		template = self.op(templatePath) if templatePath else None
		if not template:
			raise Exception('Unsupported comp type: {!r}'.format(spec.compType))
		dest = self.op('contents')
		existingComps = self._ComponentsInOrder
		i = len(existingComps)
		outName = str(self.par.Chainoutputname)
		if self._IsChain:
			inputSource = None
			if existingComps:
				if outName:
					inputSource = existingComps[-1].op(outName)
				else:
					inputSource = existingComps[-1].outputConnectors[0]
			if not inputSource:
				inputSource = self.op('contents/__chop_in')
		else:
			inputSource = None
		comp = createFromTemplate(
			template=template,
			dest=dest,
			name=spec.name or 'comp_{}'.format(i),
			attrs=OPAttrs(
				nodePos=(200, 500 - (i * 150)),
				inputs=[inputSource] if inputSource else None,
			)
		)  # type: SerializableComponentOrCOMP
		comp.SetComponentSpec(spec)
		if self._IsChain:
			if outName:
				outputSource = comp.op(outName)
			else:
				outputSource = comp.outputConnectors[0].outOP
			if comp:
				self.op('contents/__sel_chop_out').par.chop = outputSource

	@loggedmethod
	def DeleteComponent(self, comp: 'SerializableComponentOrCOMP'):
		comp.destroy()

	@loggedmethod
	def RenameComponent(self, comp: 'SerializableComponentOrCOMP', name: str):
		comp.name = name
