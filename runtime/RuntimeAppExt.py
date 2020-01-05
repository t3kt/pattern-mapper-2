from typing import Iterable

import common
from common import loggedmethod, simpleloggedmethod
from pm2_project import PProject
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.pattern_chooser.PatternChooserExt import PatternChooser
	from runtime.pattern_renderer.PatternRendererExt import PatternRenderer
	from runtime.pattern_state_manager.PatternStateManagerExt import PatternStateManager

class RuntimeApp(common.ExtensionBase):

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
		self._Chooser.SaveProject(project)

	@property
	def _Renderer(self) -> 'PatternRenderer': return self.op('pattern_renderer')

	@property
	def _Chooser(self) -> 'PatternChooser': return self.op('pattern_chooser')

	@property
	def _StateManager(self) -> 'PatternStateManager': return self.op('pattern_state_manager')

	@property
	def _SubSystems(self) -> Iterable[RuntimeSubsystem]:
		yield self._Renderer
		yield self._StateManager

	@simpleloggedmethod
	def _LoadProject(self, project: PProject):
		for comp in self._SubSystems:
			comp.ReadFromProject(project)

	def _BuildProject(self) -> PProject:
		project = PProject()
		for comp in self._SubSystems:
			comp.WriteToProject(project)
		return project
