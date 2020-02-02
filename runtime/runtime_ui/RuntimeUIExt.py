from common import loggedmethod
from pm2_messaging import Message
from pm2_runtime_shared import RuntimeComponent
from pm2_ui import UIApp

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel
	from runtime.runtime_ui.controls_panel.ControlsPanelExt import ControlsPanel
	from runtime.runtime_ui.preview_panel.PreviewPanelExt import PreviewPanel
	from runtime.runtime_ui.sources_panel.SourcesPanelExt import SourcesPanel
	from runtime.runtime_ui.state_generators_panel.StateGeneratorsPanelExt import StateGeneratorsPanel
	from runtime.RuntimeAppExt import RuntimeApp

class RuntimeUI(RuntimeComponent, UIApp):
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

	# @property
	# def ControlSettings(self): return self.op('settings_panel/control_settings_panel')

	@property
	def Sources(self) -> 'SourcesPanel': return self.op('settings_panel/sources_panel')

	@property
	def StateGenerators(self) -> 'StateGeneratorsPanel': return self.op('settings_panel/state_generators_panel')

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

	def HandleMessage(self, message: Message):
		self._LogBegin('UI MESSAGE: {}'.format(message))
		try:
			self.Controls.HandleMessage(message)
		except Exception as error:
			self._LogEvent('ERROR: {}'.format(error))
		try:
			self.Sources.HandleMessage(message)
		except Exception as error:
			self._LogEvent('ERROR: {}'.format(error))
		try:
			self.StateGenerators.HandleMessage(message)
		except Exception as error:
			self._LogEvent('ERROR: {}'.format(error))
		self._LogEnd('END UI MESSAGE: {}'.format(message))
