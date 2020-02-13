from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterable
from common import DataObject
import common

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class PPoint(DataObject):
	pos: tdu.Vector
	absDist: Optional[float] = None
	relDist: Optional[float] = None

@dataclass
class PShape(DataObject):
	shapeIndex: Optional[int] = None
	shapeName: Optional[str] = None
	shapePath: Optional[str] = None
	parentPath: Optional[str] = None
	points: List[PPoint] = field(default_factory=list)
	closed: Optional[bool] = None
	color: Optional[tdu.Color] = None
	depthLayer: Optional[int] = None
	rotateAxis: Optional[float] = None
	center: Optional[tdu.Vector] = None
	dupCount: Optional[int] = None
	pathLength: Optional[float] = None

	def pointPositions(self):
		return [point.pos for point in self.points] if self.points else []

	def centerOrAverage(self):
		return self.center or common.averageTduVectors(self.pointPositions())

	def isTriangle(self):
		return len(self.points) == 3 and self.closed

	def radius(self):
		center = self.centerOrAverage()
		return max(p.pos.distance(center) for p in self.points)

@dataclass
class PGroup(DataObject):
	groupName: str
	groupPath: Optional[str] = None
	shapeIndices: List[int] = field(default_factory=list)
	meta: Dict[str, Any] = field(default_factory=dict)
	temporary: Optional[bool] = None

	def __post_init__(self):
		self.shapeIndices = self.shapeIndices or []

@dataclass
class PSequenceStep(DataObject):
	sequenceIndex: int = 0
	shapeIndices: List[int] = field(default_factory=list)
	meta: Dict[str, Any] = field(default_factory=dict)

	def __post_init__(self):
		self.shapeIndices = self.shapeIndices or []

@dataclass
class PSequence(DataObject):
	sequenceName: str = None
	steps: List[PSequenceStep] = field(default_factory=list)
	meta: Dict[str, Any] = field(default_factory=dict)
	temporary: Optional[bool] = None

	def __post_init__(self):
		self.steps = self.steps or []

@dataclass
class PPattern(DataObject):
	width: Optional[float] = None
	height: Optional[float] = None
	scale: Optional[float] = None
	offset: Optional[tdu.Vector] = None
	shapes: List[PShape] = field(default_factory=list)
	paths: List[PShape] = field(default_factory=list)
	groups: List[PGroup] = field(default_factory=list)
	sequences: List[PSequence] = field(default_factory=list)

	def __post_init__(self):
		self.shapes = self.shapes or []
		self.paths = self.paths or []
		self.groups = self.groups or []
		self.sequences = self.sequences or []

class ModelTableWriter:
	def __init__(self, table: 'DAT'):
		self.table = table

	def writeSequences(self, sequences: Iterable[PSequence]):
		dat = self.table
		dat.clear()
		dat.appendRow([
			'sequenceName',
			'sequenceLength',
			'step_count',
			'allShapeIndices',
		])
		for sequence in sequences:
			allShapeIndices = set()
			maxIndex = 0
			for step in sequence.steps:
				allShapeIndices.update(set(step.shapeIndices))
				if step.sequenceIndex > maxIndex:
					maxIndex = step.sequenceIndex
			self._appendRow([
				sequence.sequenceName,
				(1 + maxIndex) if sequence.steps else 0,
				len(sequence.steps),
				self._formatIndexList(allShapeIndices),
			])

	def writeSequenceSteps(self, sequences: Iterable[PSequence], includeMeta=False, includeSequenceName=True):
		dat = self.table
		dat.clear()
		cols = []
		if includeSequenceName:
			cols.append('sequenceName')
		cols += [
			'stepIndex',
			'shapeIndices',
		]
		if includeMeta:
			cols.append('meta')
		dat.appendRow(cols)
		for sequence in sequences:
			if not sequence.steps:
				continue
			foundIndices = [step.sequenceIndex for step in sequence.steps]
			maxIndex = max(foundIndices)
			stepsByIndex = {
				step.sequenceIndex: step
				for step in sequence.steps
			}  # type: Dict[int, PSequenceStep]
			for i in range(maxIndex + 1):
				if i not in stepsByIndex:
					shapeIndices = ''
					metaObj = None
				else:
					shapeIndices = self._formatIndexList(stepsByIndex[i].shapeIndices)
					metaObj = stepsByIndex[i].meta
				vals = []
				if includeSequenceName:
					vals.append(sequence.sequenceName)
				vals += [
					i,
					shapeIndices,
				]
				if includeMeta:
					vals.append(
						common.toJson(metaObj, minify=True) if metaObj else '',
					)
				self._appendRow(vals)

	def writeGroups(self, groups: Iterable[PGroup]):
		dat = self.table
		dat.clear()
		dat.appendRow([
			'groupName',
			'groupPath',
			'shape_count',
			'shapeIndices',
		])
		for group in groups:
			vals = [
				group.groupName,
				group.groupPath,
				len(group.shapeIndices),
				self._formatIndexList(group.shapeIndices),
			]
			self._appendRow(vals)

	def writeShapeGroupMemberships(self, shapeTable: 'DAT', groupTable: 'DAT'):
		dat = self.table
		dat.clear()
		dat.appendCol(shapeTable.col('shapeIndex'))
		allShapeIndices = [int(shapeIndex) for shapeIndex in shapeTable.col('shapeIndex')[1:]]
		for groupRow in range(1, groupTable.numRows):
			groupName = groupTable[groupRow, 'groupName']
			groupShapeIndices = {int(shapeIndex) for shapeIndex in groupTable[groupRow, 'shapeIndices'].val.split(' ')}
			self._appendCol([groupName or ''] + [
				str(int(shapeIndex in groupShapeIndices))
				for shapeIndex in allShapeIndices
			])

	def writeShapeSequenceStepMaskTable(self, sequence: PSequence, shapeCount: int):
		dat = self.table
		dat.clear()
		if not shapeCount:
			return
		if not sequence.steps:
			dat.appendRow([0] * shapeCount)
			return
		foundIndices = [step.sequenceIndex for step in sequence.steps]
		maxIndex = max(foundIndices)
		stepsByIndex = {
			step.sequenceIndex: step
			for step in sequence.steps
		}  # type: Dict[int, PSequenceStep]
		for index in range(maxIndex + 1):
			if index not in stepsByIndex:
				self._appendRow([0] * shapeCount)
			else:
				step = stepsByIndex[index]
				self._appendRow([
					1 if shapeIndex in step.shapeIndices else 0
					for shapeIndex in range(shapeCount)
				])

	def _appendRow(self, vals: list):
		self.table.appendRow(common.formatValues(vals))

	def _appendCol(self, vals: list):
		self.table.appendCol(common.formatValues(vals))

	@staticmethod
	def _formatIndexList(indices: Iterable[int]):
		if not indices:
			return ''
		return ' '.join(map(str, sorted(indices)))

