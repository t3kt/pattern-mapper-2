from typing import List, Optional, Union

from common import createFromTemplate, OPAttrs, loggedmethod, simpleloggedmethod
from pm2_managed_components import ManagedComponentInterface
from pm2_messaging import CommonMessages, Message, MessageHandler
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_ManagedCompT = Union[SerializableComponentOrCOMP, ManagedComponentInterface]

class ComponentManager(RuntimeComponent, MessageHandler):
	@property
	def _Components(self) -> List[_ManagedCompT]:
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
		specs = []
		for comp in self._ComponentsInOrder:
			managedComp = self._GetManagedComponentInterface(comp)
			specs.append(managedComp.GetComponentSpec())
		return specs

	@staticmethod
	def _GetManagedComponentInterface(comp: 'COMP') -> _ManagedCompT:
		if hasattr(comp.ext, 'ManagedComponent'):
			return comp.ext.ManagedComponent
		else:
			return comp

	@simpleloggedmethod
	def ReadComponentSpecs(self, specs: List[PComponentSpec]):
		self.ClearComponents()
		if not specs:
			return
		for spec in specs:
			self.AddComponent(spec, deferMessageToUI=False)

	@loggedmethod
	def ClearComponents(self):
		for comp in self._Components:
			comp.destroy()
		if self._IsChain:
			self.op('contents/__sel_chop_out').par.chop = self.op('contents/__chop_in')
		self._SendMessage(CommonMessages.cleared)

	@simpleloggedmethod
	def AddComponent(self, spec: PComponentSpec, deferMessageToUI=True):
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
		)  # type: _ManagedCompT
		spec.name = comp.name  # handle the case where the name wasn't unique and was automatically changed
		if hasattr(comp.par, 'Pattern') and comp.par.Pattern.isOP:
			comp.par.Pattern.expr = 'parent.manager.par.Pattern'
		self._LogEvent('Created component {}, nodeY: {}'.format(comp, comp.nodeY))
		managedComp = self._GetManagedComponentInterface(comp)
		managedComp.SetComponentSpec(spec)
		if self._IsChain:
			self._RebuildChain()
		self._SendMessage(CommonMessages.added, [spec, comp.path], defer=deferMessageToUI)

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
	def DeleteComponent(self, comp: _ManagedCompT):
		name = comp.name
		comp.destroy()
		self._SendMessage(CommonMessages.deleted, name, defer=True)

	@loggedmethod
	def RenameComponent(self, comp: _ManagedCompT, name: str):
		oldName = comp.name
		comp.name = name
		self._RebuildChain()
		self._SendMessage(CommonMessages.renamed, data=[oldName, name], defer=True)

	def _GetComponentByName(self, name: str) -> Optional[_ManagedCompT]:
		if not name:
			return None
		comp = self.op('contents/' + name)
		if comp and comp.isCOMP:
			return comp

	def _SendMessage(self, name: str, data=None, defer=False):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		if defer:
			code = f'op({self.ownerComp.path!r}).ext.ComponentManager._SendMessage({name!r}, args, defer=False)'
			run(code, data or [], fromOP=self.ownerComp, delayFrames=1)
		else:
			handler.HandleMessage(Message(name, data, namespace=str(self.par.Messagenamespace)))

	def HandleMessage(self, message: Message):
		namespace = str(self.par.Messagenamespace)
		if not namespace or message.namespace != namespace:
			return
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
		elif message.name == CommonMessages.setPar:
			comp = self._GetComponentByName(message.data[0])
			parName = message.data[1]
			val = message.data[2]
			# self._LogEvent(f'handling setPar {message}..')
			# self._LogEvent(f'... comp: {comp!r} parName: {parName!r} val: {val!r}')
			if hasattr(comp, 'SetParVal'):
				managedComp = comp
				# self._LogEvent('.... it has a SetParVal method!')
			elif hasattr(comp.ext, 'ManagedComponent'):
				managedComp = comp.ext.ManagedComponent
				# self._LogEvent('.... it has a ManagedComponent extension!')
			else:
				# self._LogEvent('.... it does NOT have a SetParVal method!')
				return
			managedComp.SetParVal(parName, val)
