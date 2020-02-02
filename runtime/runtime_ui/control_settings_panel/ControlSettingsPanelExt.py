from pm2_messaging import Message
from pm2_runtime_shared import RuntimeComponent
from pm2_ui import UISubSystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel

class ControlSettingsPanel(RuntimeComponent, UISubSystem):
	@property
	def _ComponentManagerPanel(self) -> 'ComponentManagerPanel':
		return self.op('component_manager_panel')

	def HandleMessage(self, message: Message):
		self._ComponentManagerPanel.HandleMessage(message)
