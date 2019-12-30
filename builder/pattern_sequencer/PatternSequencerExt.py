import common
from pm2_model import PPattern, PSequenceStep, PSequence
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase, GeneratorBase, shapeAttrGetter
from typing import Optional

class PatternSequencer(PatternProcessorBase):
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		raise NotImplementedError()

class _SequenceGenerator(GeneratorBase):
	def __init__(self, hostObj, seqGenSpec: PSequenceGenSpec, logPrefix: str = None):
		super().__init__(hostObj, seqGenSpec, logPrefix or 'SeqGen')
		attrs = seqGenSpec.attrs or PSequenceGenAttrs()
		self.temporary = attrs.temporary

	@staticmethod
	def _createSequence(
			sequenceName: str,
			steps: List[PSequenceStep] = None):
		seq = PSequence(
			sequenceName,
			steps=list(steps or []),
		)
		return seq

	def generateSequences(self, pattern: PPattern):
		raise NotImplementedError()

class _AttrSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PAttrSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'AttrSeqGen')
		self.attrAccessor = shapeAttrGetter(seqGenSpec.byAttr, seqGenSpec.roundDigits)
		if not seqGenSpec.scopes:
			self.scopes = None
		else:
			self.scopes = [
				common.ValueSequence.FromSpec(scope.groups, cyclic=False)
				for scope in seqGenSpec.scopes
			]

	def generateSequences(self, pattern: PPattern):
		pass

