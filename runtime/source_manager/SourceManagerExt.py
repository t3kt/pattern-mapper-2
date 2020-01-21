from common import simpleloggedmethod, loggedmethod
from pm2_project import PProject, PComponentSpec, PSourcesSettings
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

class SourceManager(RuntimeSubsystem):
	@property
	def _ComponentManager(self) -> 'ComponentManager':
		return self.op('component_manager')

	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		specs = project.sources.sources if project.sources else []
		self._ComponentManager.ReadComponentSpecs(specs)

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		specs = self._ComponentManager.WriteComponentSpecs()
		project.sources = PSourcesSettings(sources=specs)

	@loggedmethod
	def AddSource(self, spec: PComponentSpec):
		self._ComponentManager.AddComponent(spec)
