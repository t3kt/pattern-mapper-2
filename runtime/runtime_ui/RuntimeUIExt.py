from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel

class RuntimeUI(RuntimeComponent):
	@loggedmethod
	def EditControlSettings(self, index: int):
		self._AppSettings.par.Activetab = 'controlsettings'
		panel = self.op('settings_panel/control_settings_panel').ext.ComponentManagerPanel  # type: ComponentManagerPanel
		panel.SelectComponent(index)
