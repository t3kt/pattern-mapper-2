from common import loggedmethod
from pm2_messaging import MessageHandler, Message
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel

class ControlsPanel(RuntimeComponent, MessageHandler):
	@loggedmethod
	def Initialize(self):
		self._ClearControls()

	@loggedmethod
	def RebuildControls(self, table: 'DAT'):
		# return
		self._ClearControls()
		return
		for i in range(1, table.numRows):
			self._AddControl(table, i)

	def _ClearControls(self):
		for o in self.ownerComp.ops('ctrl__*'):
			o.destroy()

	def _AddControl(self, table: 'DAT', i: int):
		panel = self.ownerComp.copy(self.op('master_control_panel'), name='ctrl__{}'.format(i))  # type: COMP
		i = panel.digits
		panel.par.clone = op(table[i, 'panel'])
		panel.par.Targetop = op(table[i, 'path'])
		panel.par.display = True
		panel.par.alignorder = i
		# panel.par.w.expr = 'me.panelParent().width / 4'
		# panel.par.h.expr = 'me.panelParent().height / 4'
		panel.nodeX = 200
		panel.nodeY = -150 * i

	@property
	def _ComponentManagerPanel(self) -> 'ComponentManagerPanel':
		return self.op('component_manager_panel')

	def HandleMessage(self, message: Message):
		self._ComponentManagerPanel.HandleMessage(message)
