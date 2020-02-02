from typing import Callable, Optional

from common import loggedmethod, createFromTemplate, OPAttrs
from pm2_messaging import CommonMessages, Message, MessageHandler
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP
import pm2_menu as menu

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

class ComponentManagerPanel(RuntimeComponent, MessageHandler):
	@property
	def _CompTable(self) -> 'DAT':
		return self.op('comp_table')

	@property
	def _TypeTable(self) -> 'DAT':
		return self.op('type_table')

	@property
	def _Manager(self) -> 'ComponentManager':
		return self.par.Manager.eval()

	def _AttachMarkerToComp(self, marker: 'COMP', targetComp: 'COMP'):
		marker.par.Targetop = targetComp
		marker.par.Nametext = targetComp.name.replace('_', ' ')
		enableParName = str(self.par.Enablepar)
		if hasattr(targetComp.par, enableParName):
			marker.par.Enabletogglevisible = True
			marker.par.Enable.bindExpr = 'op("{}").par.{}'.format(targetComp.path, enableParName)
		else:
			marker.par.Enabletogglevisible = False
		amountParName = str(self.par.Amountpar)
		if hasattr(targetComp.par, amountParName):
			marker.par.Amountslidervisible = True
			marker.par.Amount.bindExpr = 'op("{}").par.{}'.format(targetComp.path, amountParName)
		else:
			marker.par.Amountslidervisible = False

	def OnMarkerClick(self, sourceComp: 'COMP', eventType: str):
		if 'enable_toggle' in sourceComp.path or 'amount_slider' in sourceComp.path:
			return
		if sourceComp.par.parentshortcut == 'marker':
			marker = sourceComp
		else:
			marker = sourceComp.parent.marker
		if eventType == 'lselect':
			self._OnMarkerSelect(marker)
		elif eventType == 'rselect':
			self._ShowMarkerContextMenu(marker)

	def _OnMarkerSelect(self, marker: 'COMP'):
		index = marker.digits - 1
		selectedPar = self.par.Selectedcomp
		if index == selectedPar:
			selectedPar.val = -1
		else:
			selectedPar.val = index

	def _ShowMarkerContextMenu(self, marker: 'COMP'):
		items = [
			menu.Item(
				'Rename',
				lambda: self._ShowRenamePrompt(marker)),
			menu.Item(
				'Delete',
				lambda: self._DeleteComp(marker)),
		]
		menu.fromMouse().Show(
			items=items,
			autoClose=True,
		)

	@loggedmethod
	def _ShowRenamePrompt(self, marker: 'COMP'):
		targetComp = marker.par.Targetop.eval()
		def _callback(newName=None):
			if not newName:
				return
			self._LogEvent('Renaming {} to {}'.format(targetComp, newName))
			self._SendMessage(CommonMessages.rename, data=[targetComp.name, newName])
			self._AttachMarkerToComp(marker, targetComp)
		_ShowPromptDialog(
			title='Rename',
			default=targetComp.name,
			ok=_callback
		)

	def _DeleteComp(self, marker: 'COMP'):
		targetComp = marker.par.Targetop.eval()
		self._SendMessage(CommonMessages.delete, data=targetComp.name)

	@property
	def SelectedComp(self) -> Optional['SerializableComponentOrCOMP']:
		index = int(self.par.Selectedcomp)
		if index == -1:
			return None
		compTable = self._CompTable
		cell = compTable[1 + index, 'path']
		return op(cell) if cell else None

	def SelectComponent(self, index: int):
		self.par.Selectedcomp = index

	@property
	def PropertiesOp(self) -> Optional['COMP']:
		subName = self.op('comp_dropmenu').par.Value0.eval()
		comp = self.SelectedComp
		if not comp:
			return None
		if not subName or subName == 'main':
			return comp
		return comp.op(subName)

	def OnCreateClick(self):
		typeTable = self._TypeTable
		items = [
			menu.Item(text=typeTable[i, 'label'].val)
			for i in range(1, typeTable.numRows)
		]
		def _callback(info):
			index = info['index']
			typeName = typeTable[index + 1, 'typeName'].val
			self._CreateComponent(typeName)
		button = self.op('create_trigger')
		menu.fromButton(button).Show(
			items=items,
			callback=_callback,
			autoClose=True,
		)

	def _CreateComponent(self, typeName: str):
		self._SendMessage(CommonMessages.add, data=PComponentSpec(compType=typeName))
		self.op('marker_replicator').par.recreateall.pulse()

	@loggedmethod
	def _OnComponentsCleared(self):
		for o in self.ownerComp.ops('comp__*'):
			o.destroy()
		self.par.Selectedcomp = -1

	@loggedmethod
	def _OnComponentAdded(self, spec: PComponentSpec, compPath: str):
		marker = createFromTemplate(
			template=self.op('marker_template'),
			dest=self.ownerComp,
			name='comp__1',
			attrs=OPAttrs(
				parVals={
					'display': True,
					'Targetname': spec,
					'Sublabelvisible': False,
					'Sublabeltext': '',  # TODO: sub label text
					'Targetcomptype': spec.compType,
					'Typelabeltext': self._TypeTable[spec.compType, 'label'] or '',
				},
				parExprs={
					'alignorder': '20000 - me.nodeY',
				},
			))  # type: COMP
		i = marker.digits
		marker.nodeX = 400
		marker.nodeY = 500 - (i * 200)
		# TODO: get rid of this direct binding
		self._AttachMarkerToComp(marker, op(compPath))

	def _GetMarkerByName(self, name: str) -> Optional['COMP']:
		markerTable = self.op('markers_by_name')  # type: DAT
		pathCell = markerTable[name, 1]
		return self.op(pathCell) if pathCell else None

	@loggedmethod
	def _OnComponentDeleted(self, name: str):
		marker = self._GetMarkerByName(name)
		if not marker:
			return
		marker.destroy()
		# TODO : handle selection update if needed
		pass

	@loggedmethod
	def _OnComponentRenamed(self, oldName: str, newName: str):
		marker = self._GetMarkerByName(oldName)
		if not marker:
			return
		marker.par.Targetname = newName
		# TODO : handle selection update if needed
		pass

	def _SendMessage(self, name: str, data=None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(name, data, namespace=str(self.par.Messagenamespace)))

	def HandleMessage(self, message: Message):
		namespace = str(self.par.Messagenamespace)
		if not namespace or message.namespace != namespace:
			return
		if message.name == CommonMessages.added:
			spec = message.data[0]  # type: PComponentSpec
			compPath = message.data[1]
			self._OnComponentAdded(spec, compPath)
		elif message.name == CommonMessages.deleted:
			name = message.data
			self._OnComponentDeleted(name)
			pass
		elif message.name == CommonMessages.cleared:
			self._OnComponentsCleared()
		elif message.name == CommonMessages.renamed:
			oldName, newName = message.data
			self._OnComponentRenamed(oldName, newName)


def _ShowPromptDialog(
		title=None,
		text=None,
		default='',
		textentry=True,
		oktext='OK',
		canceltext='Cancel',
		ok: Callable = None,
		cancel: Callable = None):
	def _callback(info):
		if info['buttonNum'] == 1:
			if ok:
				if not textentry:
					ok()
				else:
					ok(info.get('enteredText'))
		elif info['buttonNum'] == 2:
			if cancel:
				cancel()
	dialog = op.TDResources.op('popDialog')  # type: PopDialogExt
	dialog.Open(
		title=title,
		text=text,
		textEntry=False if not textentry else (default or ''),
		buttons=[oktext, canceltext],
		enterButton=1, escButton=2, escOnClickAway=True,
		callback=_callback)
