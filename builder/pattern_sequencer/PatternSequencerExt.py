from common import mergeDicts
from pm2_model import PPattern, PSequenceStep, PSequence, PShape, PGroup
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase, GeneratorBase, shapeAttrGetter, createScopes, PatternAccessor
from typing import Optional, Dict, Any
from itertools import chain

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
		if isinstance(seqGenSpec, PPathSequenceGenSpec):
			return _PathSequenceGenerator(hostObj, seqGenSpec)
		if isinstance(seqGenSpec, PJoinSequenceGenSpec):
			return _JoinSequenceGenerator(hostObj, seqGenSpec)
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
			stepShapeIndices = []
			for shape in shapes:
				if _shapeContainsPoint(shape, testPoint.pos):
					stepShapeIndices.append(shape.shapeIndex)
			self._LogEvent('Found {} shapes for path point {} ({})'.format(
				len(stepShapeIndices), testPointIndex, testPoint.pos))
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

def _shapeContainsPoint(shape: PShape, testPoint: 'tdu.Vector') -> bool:
	testX, testY = testPoint.x, testPoint.y
	shapePoints = [(pt.pos.x, pt.pos.y) for pt in shape.points]
	nShapePoints = len(shapePoints)
	inside = False
	p1x, p1y = shapePoints[0]
	for i in range(nShapePoints + 1):
		p2x, p2y = shapePoints[i % nShapePoints]
		if testY > min(p1y, p2y):
			if testY <= max(p1y, p2y):
				if testX <= max(p1x, p2x):
					if p1y != p2y:
						xints = (testY - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
					else:
						xints = -99999999
					if p1x == p2x or testX <= xints:
						inside = not inside
		p1x, p1y = p2x, p2y
	return inside

class _JoinSequenceGenerator(_SequenceGenerator):
	def __init__(self, hostObj, seqGenSpec: PJoinSequenceGenSpec):
		super().__init__(hostObj, seqGenSpec, 'JoinSeqGen')
		self.patternAccessor = None  # type: Optional[PatternAccessor]
		self.partNames = seqGenSpec.partNames
		self.flatten = seqGenSpec.flattenParts

	def generateSequences(self, pattern: PPattern):
		self.patternAccessor = PatternAccessor(pattern)
		if not self.partNames:
			return
		steps = []
		nextIndex = 0
		for partName in self.partNames:
			part = self.patternAccessor.getGroupOrSequenceByName(partName)
			if part is None:
				nextIndex += 1
				continue
			meta = {'basedOn': partName}
			if self.flatten:
				meta['flat'] = True
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
		pattern.sequences.append(sequence)
