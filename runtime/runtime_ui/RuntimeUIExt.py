from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel
	from runtime.runtime_ui.controls_panel.ControlsPanelExt import ControlsPanel
	from runtime.runtime_ui.preview_panel.PreviewPanelExt import PreviewPanel
	from runtime.RuntimeAppExt import RuntimeApp

class RuntimeUI(RuntimeComponent):
	@loggedmethod
	def Initialize(self):
		self.Controls.Initialize()
		self.Preview.Initialize()

	@loggedmethod
	def EditControlSettings(self, index: int):
		self._AppSettings.par.Activetab = 'controlsettings'
		panel = self.op('settings_panel/control_settings_panel').ext.ComponentManagerPanel  # type: ComponentManagerPanel
		panel.SelectComponent(index)

	@property
	def Controls(self) -> 'ControlsPanel': return self.op('settings_panel/controls_panel')

	@property
	def Preview(self) -> 'PreviewPanel': return self.op('preview_panel')

	@loggedmethod
	def OnWindowHeaderButtonPush(self, button: 'COMP'):
		i = button.digits
		if i == 0:
			self._MinimizeWindow()
		elif i == 1:
			self._MaximizeWindow()
		elif i == 2:
			self._CloseWindow()

	def _MinimizeWindow(self):
		# TODO: implement minimize window
		pass

	def _MaximizeWindow(self):
		# TODO: implement maximize window
		# window = self._UIWindow
		# if window.isFill:
		# 	window.par.size = 'custom'
		# else:
		# 	window.par.size = 'fill'
		pass

	def _CloseWindow(self):
		runtimeApp = self._RuntimeApp  # type: RuntimeApp
		runtimeApp.CloseUI()

	@property
	def _UIWindow(self) -> 'windowCOMP':
		return op.PMUIWindow
