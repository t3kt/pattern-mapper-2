from typing import List, Optional

from common import createFromTemplate, OPAttrs, loggedmethod, simpleloggedmethod
from pm2_messaging import CommonMessages, Message, MessageHandler
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentManager(RuntimeComponent, MessageHandler):
	@property
	def _Components(self) -> List['SerializableComponentOrCOMP']:
		return [
			comp
			for comp in self.ops('contents/*')
			if comp.isCOMP
		]

	@property
	def _ComponentsInOrder(self):
		return list(sorted(self._Components, key=lambda c: -c.nodeY))

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
		# self._LogEvent('Found {} existing components'.format(i))
		comp = createFromTemplate(
			template=template,
			dest=dest,
			name=spec.name or 'comp_{}'.format(i),
			attrs=OPAttrs(
				nodePos=(200, 500 - (i * 150)),
			)
		)  # type: SerializableComponentOrCOMP
		self._LogEvent('Created component {}, nodeY: {}'.format(comp, comp.nodeY))
		comp.SetComponentSpec(spec)
		if self._IsChain:
			self._RebuildChain()

	def _RebuildChain(self):
		comps = self._ComponentsInOrder
		outName = str(self.par.Chainoutputname)
		prevSource = self.op('contents/__chop_in')
		for comp in comps:
			comp.inputConnectors[0].connect(prevSource)
			if outName:
				prevSource = comp.op(outName)
			else:
				prevSource = comp
		self.op('contents/__sel_chop_out').par.chop = prevSource

	@loggedmethod
	def DeleteComponent(self, comp: 'SerializableComponentOrCOMP'):
		comp.destroy()

	@loggedmethod
	def RenameComponent(self, comp: 'SerializableComponentOrCOMP', name: str):
		comp.name = name
		self._RebuildChain()

	def _GetComponentByName(self, name: str) -> Optional['COMP']:
		if not name:
			return None
		comp = self.op('contents/' + name)
		if comp and comp.isCOMP:
			return comp

	def HandleMessage(self, message: Message):
		if message.name == CommonMessages.add:
			self.AddComponent(message.data)
		elif message.name == CommonMessages.delete:
			comp = self._GetComponentByName(message.data)
			if not comp:
				return
			self.DeleteComponent(comp)
		elif message.name == CommonMessages.clear:
			self.ClearComponents()
		elif message.name == CommonMessages.rename:
			comp = self._GetComponentByName(message.data[0])
			if not comp:
				return
			self.RenameComponent(comp, message.data[1])
