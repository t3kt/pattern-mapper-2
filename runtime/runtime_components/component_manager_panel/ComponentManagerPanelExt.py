from typing import Callable, Optional, Any, Union

from common import loggedmethod, createFromTemplate, OPAttrs, simpleloggedmethod
from pm2_managed_components import ManagedComponentEditorInterface
from pm2_messaging import CommonMessages, Message, MessageHandler, MessageSender
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP
import pm2_menu as menu

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

_EditorOrCOMP = Union[ManagedComponentEditorInterface, 'COMP', None]

class ComponentManagerPanel(RuntimeComponent, MessageHandler, MessageSender):
	@property
	def _ComponentTable(self) -> 'DAT':
		return self.op('component_table')

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
		if index == self.par.Selectedcomp:
			self.SelectComponent(-1)
		else:
			self.SelectComponent(index)

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

	def _ShowRenamePrompt(self, marker: 'COMP'):
		targetComp = marker.par.Targetop.eval()
		def _callback(newName=None):
			if not newName:
				return
			self._LogEvent('Renaming {} to {}'.format(targetComp, newName))
			self.SendMessage(CommonMessages.rename, data=[targetComp.name, newName])
			self._AttachMarkerToComp(marker, targetComp)
		_ShowPromptDialog(
			title='Rename',
			default=targetComp.name,
			ok=_callback
		)

	def _DeleteComp(self, marker: 'COMP'):
		targetComp = marker.par.Targetop.eval()
		self.SendMessage(CommonMessages.delete, data=targetComp.name)

	@property
	def SelectedComp(self) -> Optional['SerializableComponentOrCOMP']:
		index = int(self.par.Selectedcomp)
		if index == -1:
			return None
		compTable = self._ComponentTable
		return self.op(compTable[1 + index, 'localPath'] or '')

	def SelectComponent(self, index: int):
		self.par.Selectedcomp = index
		editor = self.op(f'editors_panel/editor__{index + 1}')
		self.op('editors_panel').par.display = editor is not None

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
		self.SendMessage(CommonMessages.add, data=PComponentSpec(compType=typeName))

	@loggedmethod
	def _OnComponentsCleared(self):
		comps = self.ownerComp.ops('markers_panel/comp__*')
		self._LogEvent(f'Destroying markers: {comps}')
		for o in comps:
			o.destroy()
		comps = self.ownerComp.ops('editors_panel/editor__*')
		self._LogEvent(f'Destroying editors: {comps}')
		for o in comps:
			o.destroy()
		self._InitComponentTable()
		self.par.Selectedcomp = -1

	def _InitComponentTable(self):
		table = self._ComponentTable
		table.clear()
		table.appendRow(['name', 'compType', 'localPath', 'marker', 'editor'])

	def _AutoInitComponentTable(self):
		table = self._ComponentTable
		if table.numRows < 1 or table.numCols < 5 or table[0, 0] != 'name':
			self._InitComponentTable()

	@simpleloggedmethod
	def _OnComponentAdded(self, spec: PComponentSpec, compPath: str):
		self._AutoInitComponentTable()
		table = self._ComponentTable
		index = table.numRows
		self._LogEvent(f'Handling new component {spec.name}, index: {index}...')
		marker = self._CreateMarker(spec, compPath, index=index)
		editor = self._CreateEditor(spec, index=index)
		table.appendRow([
			spec.name,
			spec.compType,
			compPath,
			marker.path,
			editor.path if editor else '',
		])
		self._LogEvent(f'... created marker: {marker!r} and editor: {editor!r}')

	def _CreateMarker(self, spec: PComponentSpec, compPath: str, index: int):
		marker = createFromTemplate(
			template=self.op('marker_template'),
			dest=self.op('markers_panel'),
			name=f'comp__{index}',
			attrs=OPAttrs(
				parVals={
					'display': True,
					'Targetname': spec.name,
					'Sublabelvisible': False,
					'Sublabeltext': '',  # TODO: sub label text
					'Targetcomptype': spec.compType,
					'Typelabeltext': self._TypeTable[spec.compType, 'label'] or '',
				},
				parExprs={
					'Selected': f'(parent.managerPanel.par.Selectedcomp+1) == {index}',
					'alignorder': '20000 - me.nodeY',
				},
				nodePos=(400, 500 - (index * 200)),
			))  # type: COMP
		# TODO: get rid of this direct binding
		self._AttachMarkerToComp(marker, op(compPath))
		return marker

	def _CreateEditor(self, spec: PComponentSpec, index: int):
		template = self._GetEditorTemplateForType(spec.compType)
		if not template:
			return
		editor = createFromTemplate(
			template=template,
			dest=self.op('editors_panel'),
			name=f'editor__{index}',
			attrs=OPAttrs(
				parVals={
					'hmode': 'fill',
					'vmode': 'fill',
				},
				parExprs={
					'display': f'(parent.managerPanel.par.Selectedcomp+1) == {index}',
					'alignorder': '20000 - me.nodeY',
				},
				nodePos=(400, 500 - (index * 200)),
			)
		)  # type: _EditorOrCOMP
		editor.initializeExtensions()
		if hasattr(editor, 'InitializeEditor'):
			editorExt = editor
		elif hasattr(editor.ext, 'ManagedEditor'):
			editorExt = editor.ext.ManagedEditor
		else:
			self._LogEvent(f'ERROR: UNSUPPORTED EDITOR: {editor}')
			return
		editorExt.InitializeEditor(
			namespace=str(self.par.Messagenamespace),
			messageHandler=self.par.Messagehandler.eval(),
			spec=spec,
		)
		return editor

	def _GetMarkerByName(self, name: str) -> Optional['COMP']:
		return self.op(self._ComponentTable[name, 'marker'] or '')

	def _GetEditorByName(self, name: str) -> _EditorOrCOMP:
		return self.op(self._ComponentTable[name, 'editor'] or '')

	def _GetEditorTemplateForType(self, compType: str):
		return self.op(self._TypeTable[compType, 'editor'] or '')

	@loggedmethod
	def _OnComponentDeleted(self, name: str):
		marker = self._GetMarkerByName(name)
		editor = self._GetEditorByName(name)
		if marker:
			marker.destroy()
		if editor:
			editor.destroy()
		self._ComponentTable.deleteRow(name)
		# TODO : handle selection update if needed
		pass

	@loggedmethod
	def _OnComponentRenamed(self, oldName: str, newName: str):
		oldLocalPath = self._ComponentTable[oldName, 'localPath']
		if oldLocalPath:
			newLocalPath = oldLocalPath.val.rsplit('/', maxsplit=1)[0] + '/' + newName
			self._ComponentTable[oldName, 'localPath'] = newLocalPath
		marker = self._GetMarkerByName(oldName)
		editor = self._GetEditorByName(oldName)
		if marker:
			marker.par.Targetname = newName
			marker.name = newName
			self._ComponentTable[oldName, 'marker'] = marker.path
		if editor:
			if hasattr(editor, 'SetTargetName'):
				editorExt = editor
			elif hasattr(editor.ext, 'ManagedEditor'):
				editorExt = editor.ext.ManagedEditor
			else:
				self._LogEvent(f'ERROR: UNSUPPORTED EDITOR: {editor}')
				editorExt = None
			if editorExt:
				editorExt.SetTargetName(newName)
			editor.name = newName
			self._ComponentTable[oldName, 'editor'] = editor.path
		self._ComponentTable[oldName, 'name'] = newName
		# TODO : handle selection update if needed
		pass

	def _OnComponentParValReceived(self, name: str, parName: str, val: Any):
		editor = self._GetEditorByName(name)
		if not editor:
			return
		editor.SetParVal(parName, val)

	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(
			name,
			data,
			namespace=namespace or str(self.par.Messagenamespace)))

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
		elif message.name == CommonMessages.parVal:
			compName = message.data[0]
			parName = message.data[1]
			val = message.data[2]
			self._OnComponentParValReceived(compName, parName, val)



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
