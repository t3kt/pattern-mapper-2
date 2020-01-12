from typing import List

from common import createFromTemplate, OPAttrs, simpleloggedmethod, loggedmethod
from pm2_project import PProject, PComponentSpec, PSourcesSettings
from pm2_runtime_shared import RuntimeSubsystem, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SourceManager(RuntimeSubsystem):
	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		specs = project.sources.sources if project.sources else []
		self._ClearSources()
		for spec in specs:
			self.AddSource(spec)

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		specs = [
			comp.GetComponentSpec()
			for comp in self._Sources
		]
		project.sources = PSourcesSettings(sources=specs)

	def _GetTemplate(self, compType: str):
		templates = self.op('template_table')
		cell = templates[compType, 'path']
		template = self.op(cell)
		if not template:
			raise Exception('Unsupported component type: {!r}'.format(compType))
		return template

	@property
	def _SourcesHolder(self): return self.op('sources')

	@property
	def _Sources(self) -> List[SerializableComponentOrCOMP]:
		return self._SourcesHolder.ops('src__*')

	@loggedmethod
	def AddSource(self, spec: PComponentSpec):
		template = self._GetTemplate(spec.compType)
		if not template:
			return
		dest = self._SourcesHolder
		existing = self._Sources
		i = len(existing)
		comp = createFromTemplate(
			template=template,
			dest=dest,
			name='src__{}'.format(i),
			attrs=OPAttrs(
				nodePos=(200, 500 - (i * 150)),
			),
		)  # type: SerializableComponentOrCOMP
		comp.SetComponentSpec(spec)

	def _ClearSources(self):
		for comp in self._Sources:
			comp.destroy()
