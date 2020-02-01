from pm2_messaging import MessageHandler, Message
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel

class SourcesPanel(RuntimeComponent, MessageHandler):
	@property
	def _ComponentManagerPanel(self) -> 'ComponentManagerPanel':
		return self.op('component_manager_panel')

	def HandleMessage(self, message: Message):
		self._ComponentManagerPanel.HandleMessage(message)
