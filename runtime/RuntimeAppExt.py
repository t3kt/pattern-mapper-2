from typing import Iterable, Union

import common
from common import loggedmethod, simpleloggedmethod
from pm2_project import PProject
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.control_manager.ControlManagerExt import ControlManager
	from runtime.pattern_chooser.PatternChooserExt import PatternChooser
	from runtime.pattern_renderer.PatternRendererExt import PatternRenderer
	from runtime.pattern_state_manager.PatternStateManagerExt import PatternStateManager
	from runtime.source_manager.SourceManagerExt import SourceManager
	from runtime.runtime_ui.RuntimeUIExt import RuntimeUI
	from runtime.app_settings.AppSettingsExt import AppSettings

class RuntimeApp(common.ExtensionBase):
	def OnStartup(self):
		self._LogBegin('OnStartup')
		try:
			self.Settings.Initialize()
			if self.Settings.par.Autoinitialize:
				self.Initialize()
		finally:
			self._LogEnd('OnStartup')

	def Initialize(self):
		self._LogBegin('Initialize')
		try:
			self.SourceManager.Initialize()
			self.ControlManager.Initialize()
			self.UI.Initialize()
			self.ShowPatternChooser()
		finally:
			self._LogEnd('Initialize')

	def ShowPatternChooser(self):
		self.op('pattern_chooser_window').par.winopen.pulse()

	def ClosePatternChooser(self):
		self.op('pattern_chooser_window').par.winclose.pulse()

	def ShowUI(self):
		self.op('ui_window').par.winopen.pulse()

	def CloseUI(self):
		self.op('ui_window').par.winclose.pulse()

	@loggedmethod
	def OnChoosePattern(self):
		self.op('pattern_loader').par.Extract.pulse()
		projectJson = self.op('project_json').text or '{}'
		project = PProject.parseJsonStr(projectJson)
		self._LoadProject(project)
		self.ClosePatternChooser()
		self.ShowUI()

	def SaveProject(self):
		project = self._BuildProject()
		self.Chooser.SaveProject(project)

	@property
	def Settings(self) -> Union['COMP', 'AppSettings']: return op.PMSettings

	@property
	def UI(self) -> 'RuntimeUI': return self.op('runtime_ui')

	@property
	def Renderer(self) -> 'PatternRenderer': return self.op('pattern_renderer')

	@property
	def Chooser(self) -> 'PatternChooser': return self.op('pattern_chooser')

	@property
	def StateManager(self) -> 'PatternStateManager': return self.op('pattern_state_manager')

	@property
	def SourceManager(self) -> 'SourceManager': return self.op('source_manager')

	@property
	def ControlManager(self) -> 'ControlManager': return self.op('control_manager')

	@property
	def _SubSystems(self) -> Iterable[RuntimeSubsystem]:
		yield self.Renderer
		yield self.StateManager
		yield self.SourceManager
		yield self.ControlManager

	@simpleloggedmethod
	def _LoadProject(self, project: PProject):
		for comp in self._SubSystems:
			comp.ReadFromProject(project)

	def _BuildProject(self) -> PProject:
		project = PProject()
		for comp in self._SubSystems:
			comp.WriteToProject(project)
		return project
