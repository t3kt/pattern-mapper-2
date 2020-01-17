from pm2_model import PPattern, PSequenceStep, PSequence, PShape
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase, GeneratorBase, shapeAttrGetter, createScopes, PatternAccessor
from typing import Optional, Dict, Any

class PatternSequencer(PatternProcessorBase):
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		if not pattern.sequences:
			pattern.sequences = []
		if settings and settings.sequencing and settings.sequencing.sequenceGenerators:
			for spec in settings.sequencing.sequenceGenerators:
				self._LogEvent('using sequence generator {}({})'.format(type(spec), spec))
				generator = _SequenceGenerator.fromSpec(self, spec)
				generator.generateSequences(pattern)
		self._LogEvent('Generated {} sequences: {}'.format(
			len(pattern.sequences), [seq.sequenceName for seq in pattern.sequences]))
		return pattern

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

	@classmethod
	def fromSpec(cls, hostObj, seqGenSpec: PSequenceGenSpec):
		if isinstance(seqGenSpec, PAttrSequenceGenSpec):
			return _AttrSequenceGenerator(hostObj, seqGenSpec)
		raise Exception('Unsupported sequence gen spec type: {}'.format(type(seqGenSpec)))

class _AttrSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PAttrSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'AttrSeqGen')
		self.attrAccessor = shapeAttrGetter(seqGenSpec.byAttr, seqGenSpec.roundDigits)
		self.scopes = createScopes(seqGenSpec.scopes)

	def generateSequences(self, pattern: PPattern):
		if not self.scopes:
			sequences = [self._generateSeqForShapes(pattern.shapes, None)]
		else:
			patternAccessor = PatternAccessor(pattern)
			sequences = []
			for scopeIndex, scope in enumerate(self.scopes):
				shapeIndices = patternAccessor.getShapeIndicesByGroupPattern(scope)
				shapes = patternAccessor.getShapesByIndices(shapeIndices)
				sequence = self._generateSeqForShapes(shapes, scopeIndex)
				if sequence is not None:
					sequences.append(sequence)
		if not sequences:
			return
		pattern.sequences += sequences

	def _generateSeqForShapes(self, shapes: List[PShape], scopeIndex: Optional[int]):
		bins = {}  # type: Dict[Any, List[int]]
		for shape in shapes:
			attrVal = self.attrAccessor(shape)
			if attrVal is None:
				continue
			if attrVal in bins:
				bins[attrVal].append(shape.shapeIndex)
			else:
				bins[attrVal] = [shape.shapeIndex]
		if not bins:
			return None
		steps = []
		for key in sorted(bins.keys()):
			stepShapeIndices = bins[key]
			steps.append(PSequenceStep(
				sequenceIndex=len(steps),
				shapeIndices=stepShapeIndices,
				meta={'attrValue': key}
			))
		return self._createSequence(
			sequenceName=self._getName(scopeIndex or 0, isSolo=scopeIndex is None),
			steps=steps,
		)

