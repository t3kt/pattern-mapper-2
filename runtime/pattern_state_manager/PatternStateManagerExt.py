from typing import List

from common import createFromTemplate, OPAttrs, loggedmethod, simpleloggedmethod
from pm2_project import PProject, PComponentSpec, PStateGenSettings
from pm2_runtime_shared import RuntimeSubsystem, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternStateManager(RuntimeSubsystem):
	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		self._ClearStateGenerators()
		if project.state and project.state.generators:
			for spec in project.state.generators:
				self.AddStateGenerator(spec)

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		specs = []
		for gen in self._Generators:
			spec = gen.GetComponentSpec()
			specs.append(spec)
		project.state = PStateGenSettings(generators=specs)

	@property
	def _GeneratorChain(self):
		return self.op('generator_chain')

	@property
	def _Generators(self) -> List[SerializableComponentOrCOMP]:
		return self._GeneratorChain.ops('gen__*')

	def _GetTemplate(self, compType: str):
		templates = self.op('template_table')
		cell = templates[compType, 'path']
		template = self.op(cell)
		if not template:
			raise Exception('Unsupported component type: {!r}'.format(compType))
		return template

	@loggedmethod
	def AddStateGenerator(self, spec: PComponentSpec):
		template = self._GetTemplate(spec.compType)
		if not template:
			return
		existingGenerators = self._Generators
		i = len(existingGenerators)
		dest = self._GeneratorChain
		gen = createFromTemplate(
			template=template,
			dest=dest,
			name='gen__{}'.format(i),
			attrs=OPAttrs(
				nodePos=(200, 500 - (i * 150)),
				inputs=[
					existingGenerators[-1].outputConnectors[0] if existingGenerators else dest.op('input_shape_states'),
				],
			),
		)  # type: SerializableComponentOrCOMP
		gen.SetComponentSpec(spec)
		dest.op('sel_output_shape_states').par.chop = gen.op('shape_states_out')

	def _ClearStateGenerators(self):
		for gen in self._Generators:
			gen.destroy()
		chain = self._GeneratorChain
		chain.op('sel_output_shape_states').par.chop = chain.op('input_shape_states')
