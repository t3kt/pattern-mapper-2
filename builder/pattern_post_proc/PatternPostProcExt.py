from collections import deque

import common
from common import simpleloggedmethod
from pm2_model import PPattern, PShape, PGroup
from pm2_settings import PSettings, PDuplicateMergeSettings, ShapeEquivalence, PScope
from pm2_builder_shared import PatternProcessorBase, PatternAccessor
from typing import Dict, Iterable, List, Set

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternPostProcessor(PatternProcessorBase):
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		processor = _PostProcessor(self, settings)
		processor.process(pattern)
		return pattern

class _PostProcessor(common.LoggableSubComponent):
	def __init__(self, hostObj, settings: PSettings):
		super().__init__(hostObj, logprefix='PostProc')
		self.settings = settings or PSettings()
		self.pattern = PPattern()

	@simpleloggedmethod
	def process(self, pattern: PPattern):
		self.pattern = pattern
		if self.settings.dedup:
			self._deduplicateShapes()

	@simpleloggedmethod
	def _deduplicateShapes(self):
		dedup = _ShapeDeduplicator(self, self.pattern, self.settings.dedup)
		dedup.mergeDuplicates()

def _createScopes(scopeSpecs: List[PScope]):
	if not scopeSpecs:
		return None
	return [
		common.ValueSequence.FromSpec(scope.groups, cyclic=False)
		for scope in scopeSpecs
	]

class _ShapeDeduplicator(common.LoggableSubComponent):
	def __init__(self, hostObj, pattern: PPattern, dedupSettings: PDuplicateMergeSettings):
		super().__init__(hostObj, logprefix='ShapeDedup')
		self.pattern = pattern
		self.patternAccessor = PatternAccessor(pattern)
		self.comparator = _ShapeComparator(dedupSettings)
		self.primaryScopes = _createScopes(dedupSettings.primaryScopes)
		if not self.primaryScopes:
			self.primaryShapeIndices = None
		else:
			self.primaryShapeIndices = set()  # type: Set[int]
		self.scopes = _createScopes(dedupSettings.scopes)
		self.dupRemappers = []  # type: List[_ShapeIndexRemapper]

	@simpleloggedmethod
	def mergeDuplicates(self):
		self._loadPrimaryShapes()
		self._loadDuplicates()
		self._LogEvent('Found {} remapper scopes'.format(len(self.dupRemappers)))
		modified = False
		for remapper in self.dupRemappers:
			self._LogEvent('Found {} shapes to replace'.format(len(remapper)))
			if remapper:
				if remapper.remapShapesInGroups(self.pattern):
					modified = True
		if modified:
			self._removeDuplicateShapes()

	def _loadPrimaryShapes(self):
		if self.primaryShapeIndices is None:
			return
		for scope in self.primaryScopes:
			shapeIndices = self.patternAccessor.getShapeIndicesByGroupPattern(scope)
			if shapeIndices:
				self.primaryShapeIndices.update(set(shapeIndices))
		self._LogEvent('Found {} primary shapes'.format(len(self.primaryShapeIndices)))

	def _loadDuplicates(self):
		if not self.scopes:
			self.dupRemappers = [self._loadDupRemapperForShapes(self.pattern.shapes)]
		else:
			self.dupRemappers = []
			for scope in self.scopes:
				shapeIndices = self.patternAccessor.getShapeIndicesByGroupPattern(scope)
				shapes = [shape for shape in self.pattern.shapes if shape.shapeIndex in shapeIndices]
				if shapes:
					self.dupRemappers.append(self._loadDupRemapperForShapes(shapes))

	def _primaryShapesFirst(self, shapes: Iterable[PShape]):
		if not self.primaryShapeIndices:
			return list(shapes)
		resultShapes = [
			shape
			for shape in shapes
			if shape.shapeIndex in self.primaryShapeIndices
		]
		resultShapes += [
			shape
			for shape in shapes
			if shape.shapeIndex not in self.primaryShapeIndices
		]
		return resultShapes

	def _loadDupRemapperForShapes(self, shapes: List[PShape]):
		remapper = _ShapeIndexRemapper(self, 'DeDup')
		shapes = self._primaryShapesFirst(shapes)
		for i, shape1 in enumerate(shapes):
			if shape1.shapeIndex in remapper:
				continue
			dupsForShape = []
			for shape2 in shapes[i + 1:]:
				if self.comparator.shapesEquivalent(shape1, shape2):
					remapper[shape2.shapeIndex] = shape1.shapeIndex
					dupsForShape.append(shape2.shapeIndex)
					shape2.dupCount = -1
			if dupsForShape:
				self._LogEvent('Found duplicates for shape {}: {}'.format(shape1.shapeIndex, dupsForShape))
				shape1.dupCount = len(dupsForShape)
		return remapper

	def _removeDuplicateShapes(self):
		self._LogEvent('Removing {} duplicate shapes'.format(sum([len(remapper) for remapper in self.dupRemappers])))
		remainingShapes = []
		removedShapeCount = 0
		remapper = _ShapeIndexRemapper(self, 'ReIndex')
		shapes = self._primaryShapesFirst(self.pattern.shapes)
		for shape in shapes:
			if shape.dupCount == -1:
				removedShapeCount += 1
			else:
				oldIndex = shape.shapeIndex
				shape.shapeIndex = len(remainingShapes)
				remainingShapes.append(shape)
				if shape.shapeIndex != oldIndex:
					remapper[oldIndex] = shape.shapeIndex
		if not remapper:
			self._LogEvent('No renumbering needed')
			return False
		self._LogEvent('Removing {} shapes, {} remaining'.format(removedShapeCount, len(remainingShapes)))
		self.pattern.shapes = remainingShapes
		remapper.remapShapesInGroups(self.pattern)
		return True

class _ShapeComparator:
	def __init__(self, dedupSettings: PDuplicateMergeSettings):
		self.tolerance = dedupSettings.tolerance or 0.0
		self.equivalence = dedupSettings.equivalence
		self.ignoreDepth = dedupSettings.ignoreDepth

	def _distance(self, vec1: tdu.Vector, vec2: tdu.Vector):
		if self.ignoreDepth:
			return tdu.Vector(vec1.x, vec2.y, 0).distance(tdu.Vector(vec2.x, vec2.y, 0))
		return vec1.distance(vec2)

	def _vectorsEquivalent(self, vec1: tdu.Vector, vec2: tdu.Vector):
		return self._distance(vec1, vec2) <= self.tolerance

	def shapesEquivalent(self, shape1: PShape, shape2: PShape):
		n = len(shape1.points)
		if n != len(shape2.points):
			return False
		if self.equivalence == ShapeEquivalence.points:
			return self._shapesEquivalentByUnalignedPoints(shape1, shape2)
		if self.equivalence == ShapeEquivalence.alignedPoints:
			return self._shapesEquivalentByAlignedPoints(shape1, shape2)
		return self._shapesEquivalentByCenterRadius(shape1, shape2)

	def _shapesEquivalentByCenterRadius(self, shape1: PShape, shape2: PShape):
		if not self._vectorsEquivalent(shape1.centerOrAverage(), shape2.centerOrAverage()):
			return False
		return abs(shape1.radius() - shape2.radius()) <= self.tolerance

	def _shapesEquivalentByAlignedPoints(self, shape1: PShape, shape2: PShape):
		return self._vectorSequencesEquivalent(shape1.pointPositions(), shape2.pointPositions())

	def _shapesEquivalentByUnalignedPoints(self, shape1: PShape, shape2: PShape):
		positions1 = shape1.pointPositions()
		positions2 = shape2.pointPositions()
		offset = None
		for i, pos2 in enumerate(positions2):
			if self._vectorsEquivalent(positions1[0], pos2):
				offset = i
				break
		if offset is None:
			return False
		positions2 = deque(positions2)
		positions2.rotate(offset)
		return self._vectorSequencesEquivalent(positions1, positions2)

	def _vectorSequencesEquivalent(self, positions1: Iterable[tdu.Vector], positions2: Iterable[tdu.Vector]):
		for pos1, pos2 in zip(positions1, positions2):
			if not self._vectorsEquivalent(pos1, pos2):
				return False
		return True

class _ShapeIndexRemapper(common.LoggableSubComponent):
	def __init__(self, hostObj, logprefix='ShapeRemap'):
		super().__init__(hostObj, logprefix=logprefix)
		self.oldtonewindex = {}  # type: Dict[int, int]

	def __getitem__(self, oldindex):
		return self.oldtonewindex.get(oldindex)

	def __setitem__(self, oldindex, newindex):
		self.oldtonewindex[oldindex] = newindex

	def __contains__(self, oldindex):
		return oldindex in self.oldtonewindex

	def __len__(self):
		return len(self.oldtonewindex)

	def __bool__(self):
		return bool(self.oldtonewindex)

	def remapShapesInGroups(self, pattern: PPattern):
		modified = False
		for group in pattern.groups:
			if self._remapShapesInGroup(group):
				modified = True
		return modified

	def _remapShapesInGroup(self, group: PGroup):
		modified = _replaceIndices(group.shapeIndices, self.oldtonewindex)
		if modified:
			self._LogEvent('Replaced indices in group {}'.format(group.groupName))
		else:
			self._LogEvent('No changes in group {}'.format(group.groupName))
		return modified


def _replaceIndices(indexlist: List[int], replacements: Dict[int, int]):
	if not indexlist:
		return False
	newlist = []
	modified = False
	for index in indexlist:
		if index not in replacements:
			newlist.append(index)
		else:
			newindex = replacements[index]
			if newindex not in newlist:
				newlist.append(newindex)
			modified = True
	if not modified:
		return False
	newlist.sort()
	indexlist[:] = newlist
	return True
