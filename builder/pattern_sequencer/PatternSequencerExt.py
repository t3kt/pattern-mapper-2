from common import mergeDicts
from pm2_model import PPattern, PSequenceStep, PSequence, PShape, PGroup
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase, GeneratorBase, shapeAttrGetter, createScopes, PatternAccessor
from typing import Optional, Dict, Any

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

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

	def _createSequence(
			self,
			sequenceName: str,
			steps: List[PSequenceStep] = None):
		seq = PSequence(
			sequenceName,
			steps=list(steps or []),
			temporary=self.temporary,
		)
		return seq

	def generateSequences(self, pattern: PPattern):
		raise NotImplementedError()

	@classmethod
	def fromSpec(cls, hostObj, seqGenSpec: PSequenceGenSpec):
		if isinstance(seqGenSpec, PAttrSequenceGenSpec):
			return _AttrSequenceGenerator(hostObj, seqGenSpec)
		if isinstance(seqGenSpec, PPathSequenceGenSpec):
			return _PathSequenceGenerator(hostObj, seqGenSpec)
		if isinstance(seqGenSpec, PJoinSequenceGenSpec):
			return _JoinSequenceGenerator(hostObj, seqGenSpec)
		if isinstance(seqGenSpec, PParallelSequenceGenSpec):
			return _ParallelSequenceGenerator(hostObj, seqGenSpec)
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

class _PathSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PPathSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'PathSeqGen')
		self.scopes = createScopes(seqGenSpec.scopes)
		self.pathPath = seqGenSpec.pathPath
		self.patternAccessor = None  # type: Optional[PatternAccessor]
		self.pathShape = None  # type: Optional[PShape]

	def generateSequences(self, pattern: PPattern):
		self.patternAccessor = PatternAccessor(pattern)
		self.pathShape = self.patternAccessor.getPathByPath(self.pathPath)
		if not self.pathShape:
			self._LogEvent('Path not found: {}'.format(self.pathPath))
			return
		if not self.scopes:
			sequences = [self._generateSeqForShapes(pattern.shapes, None)]
		else:
			sequences = []
			for scopeIndex, scope in enumerate(self.scopes):
				shapeIndices = self.patternAccessor.getShapeIndicesByGroupPattern(scope)
				shapes = self.patternAccessor.getShapesByIndices(shapeIndices)
				sequence = self._generateSeqForShapes(shapes, scopeIndex)
				if sequence is not None:
					sequences.append(sequence)
		if not sequences:
			return
		pattern.sequences += sequences

	def _generateSeqForShapes(self, shapes: List[PShape], scopeIndex: Optional[int]):
		steps = []
		for testPointIndex, testPoint in enumerate(self.pathShape.points):
			stepShapes = self.patternAccessor.getShapesContainingPoint(
				testPoint.pos, predicate=lambda s: s in shapes
			)
			stepShapeIndices = [
				shape.shapeIndex
				for shape in stepShapes
			]
			# self._LogEvent('Found {} shapes for path point {} ({})'.format(
			# 	len(stepShapeIndices), testPointIndex, testPoint.pos))
			steps.append(PSequenceStep(
				sequenceIndex=testPointIndex,
				shapeIndices=stepShapeIndices,
				meta={
					'pathPath': self.pathPath,
					'pathPoint': testPointIndex,
				}
			))
		return self._createSequence(
			sequenceName=self._getName(scopeIndex or 0, isSolo=scopeIndex is None),
			steps=steps,
		)

class _JoinSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PJoinSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'JoinSeqGen')
		self.partNames = seqGenSpec.partNames
		self.flatten = seqGenSpec.flattenParts

	def generateSequences(self, pattern: PPattern):
		patternAccessor = PatternAccessor(pattern)
		if not self.partNames:
			return
		steps = []
		nextIndex = 0
		usedPartNames = []
		for partName in self.partNames:
			part = patternAccessor.getGroupOrSequenceByName(partName)
			if part is None:
				nextIndex += 1
				continue
			usedPartNames.append(partName)
			meta = {'basedOn': partName}
			if self.flatten or isinstance(part, PGroup):
				if isinstance(part, PGroup):
					shapeIndices = part.shapeIndices
				else:
					shapeIndices = [
						shapeIndex
						for step in part.steps
						for shapeIndex in step.shapeIndices
					]
				steps.append(PSequenceStep(
					sequenceIndex=nextIndex,
					shapeIndices=list(sorted(shapeIndices)),
					meta=meta
				))
				nextIndex += 1
			else:
				baseIndex = nextIndex
				for step in part.steps:
					nextIndex = baseIndex + step.sequenceIndex
					steps.append(PSequenceStep(
						sequenceIndex=nextIndex,
						shapeIndices=list(sorted(step.shapeIndices)),
						meta=mergeDicts({'basedOnStep': step.sequenceIndex}, meta)
					))
		if not steps:
			return
		sequence = self._createSequence(
			self._getName(0, isSolo=True),
			steps,
		)
		sequence.meta['basedOn'] = ' '.join(usedPartNames)
		if self.flatten:
			sequence.meta['flat'] = True
		pattern.sequences.append(sequence)

class _ParallelSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PParallelSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'ParallelSeqGen')
		self.patternAccessor = None  # type: Optional[PatternAccessor]
		self.partNames = seqGenSpec.partNames

	def generateSequences(self, pattern: PPattern):
		patternAccessor = PatternAccessor(pattern)
		if not self.partNames:
			return
		shapesByIndex = {}  # type: Dict[int, List[int]]
		partNamesByIndex = {}  # type: Dict[int, List[str]]
		usedPartNames = []
		for partName in self.partNames:
			part = patternAccessor.getGroupOrSequenceByName(partName)
			if part is None:
				continue
			usedPartNames.append(partName)
			if isinstance(part, PGroup):
				if 0 not in partNamesByIndex:
					partNamesByIndex[0] = []
				partNamesByIndex[0].append(partName)
				if 0 not in shapesByIndex:
					shapesByIndex[0] = []
				shapesByIndex[0] += list(part.shapeIndices)
			else:
				for step in part.steps:
					if step.sequenceIndex not in partNamesByIndex:
						partNamesByIndex[step.sequenceIndex] = []
					partNamesByIndex[step.sequenceIndex].append('{}.{}'.format(partName, step.sequenceIndex))
					if step.sequenceIndex not in shapesByIndex:
						shapesByIndex[step.sequenceIndex] = []
					shapesByIndex[step.sequenceIndex] += list(step.shapeIndices)
		if not shapesByIndex:
			maxIndex = 0
		else:
			maxIndex = max(shapesByIndex.keys())
		steps = []
		for i in range(maxIndex + 1):
			if i in shapesByIndex:
				steps.append(PSequenceStep(
					sequenceIndex=i,
					shapeIndices=list(sorted(set(shapesByIndex[i]))),
					meta={'basedOn': ' '.join(partNamesByIndex[i])}
				))
		if not steps:
			return
		sequence = self._createSequence(
			self._getName(0, isSolo=True),
			steps,
		)
		sequence.meta['basedOn'] = ' '.join(usedPartNames)
		pattern.sequences.append(sequence)
