from typing import Callable, Optional

from common import loggedmethod
from pm2_messaging import CommonMessages, Message, MessageHandler
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP
import pm2_menu as menu

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager
	from runtime.RuntimeAppExt import RuntimeApp

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

	def OnMarkerReplicate(self, marker: 'COMP'):
		marker.par.display = True
		i = marker.digits
		compTable = self._CompTable
		targetComp = op(compTable[i, 'path'])
		subLabelParName = str(self.par.Sublabelpar)
		subLabelPar = getattr(targetComp.par, subLabelParName) if subLabelParName else None
		if subLabelPar is None:
			marker.par.Sublabelvisible = False
		else:
			marker.par.Sublabelvisible = True
			marker.par.Sublabeltext = subLabelPar
		typeTable = self._TypeTable
		typeName = compTable[i, 'compType']
		marker.par.Targetcomptype = typeName
		marker.par.Typelabeltext = typeTable[typeName, 'label']
		self._AttachMarkerToComp(marker, targetComp)

	def _AttachMarkerToComp(self, marker: 'COMP', targetComp: 'COMP'):
		marker.par.Targetop = targetComp
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

	def _SendMessage(self, name: str, data=None):
		runtimeApp = self._RuntimeApp  # type: RuntimeApp
		runtimeApp.HandleMessage(Message(name, data, namespace=str(self.par.Messagenamespace)))

	def HandleMessage(self, message: Message):
		pass


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
