from common import loggedmethod, simpleloggedmethod
from pm2_messaging import Message, MessageHandler
from pm2_project import PProject, PComponentSpec, PStateGenSettings
from pm2_runtime_shared import RuntimeSubsystem, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

class PatternStateManager(RuntimeSubsystem, MessageHandler):
	@loggedmethod
	def Initialize(self):
		# hack for mysterious input disconnection bug
		self.op('state_channel_filter').par.reinitnet.pulse()
		pass

	@property
	def _StateFilter(self) -> 'SerializableParams':
		return self.op('state_channel_filter')

	@property
	def _ComponentManager(self) -> 'ComponentManager':
		return self.op('component_manager')

	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		self._ComponentManager.ReadComponentSpecs(
			project.state.generators if project.state and project.state.generators else [])
		self._StateFilter.SetParDict(project.state.filterPars if project.state and project.state.filterPars else {})

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		specs = self._ComponentManager.WriteComponentSpecs()
		project.state = PStateGenSettings(
			generators=specs,
			filterPars=self._StateFilter.GetParDict(),
		)

	@loggedmethod
	def AddStateGenerator(self, spec: PComponentSpec):
		self._ComponentManager.AddComponent(spec)

	def HandleMessage(self, message: Message):
		self._ComponentManager.HandleMessage(message)

