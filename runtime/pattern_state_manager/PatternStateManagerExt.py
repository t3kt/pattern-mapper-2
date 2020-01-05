from typing import Union, List

from common import createFromTemplate, OPAttrs
from pm2_project import PProject, POverrideShapeStateSpec
from pm2_runtime_shared import RuntimeSubsystem, ShapeStateGeneratorBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_GeneratorT = Union[COMP, ShapeStateGeneratorBase]

class PatternStateManager(RuntimeSubsystem):
	def ReadFromProject(self, project: PProject):
		self._ClearStateGenerators()
		for spec in project.stateGenerators or []:
			self._AddStateGenerator(spec)

	def WriteToProject(self, project: PProject):
		specs = []
		for gen in self._Generators:
			spec = gen.GetSpec()
			specs.append(spec)
		project.stateGenerators = specs

	@property
	def _GeneratorChain(self):
		return self.op('generator_chain')

	@property
	def _Generators(self) -> List[_GeneratorT]:
		return self._GeneratorChain.ops('gen__*')

	def _AddStateGenerator(self, spec):
		if isinstance(spec, POverrideShapeStateSpec):
			template = self.op('templates/group_shape_state_override')
		else:
			raise Exception('Unsupported state gen type: {!r}'.format(spec))
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
					existingGenerators[-1] if existingGenerators else dest.op('input_shape_states'),
				],
			),
		)  # type: _GeneratorT
		gen.SetSpec(spec)
		dest.op('sel_output_shape_states').par.chop = gen.op('shape_states_out')

	def _ClearStateGenerators(self):
		for gen in self._Generators:
			gen.destroy()
		chain = self._GeneratorChain
		chain.op('sel_output_shape_states').par.chop = chain.op('input_shape_states')
