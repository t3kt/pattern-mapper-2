import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from common import DataObject
import common

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class PPoint(DataObject):
	pos: tdu.Vector

@dataclass
class PShape(DataObject):
	shapeIndex: Optional[int] = None
	shapeName: Optional[str] = None
	path: Optional[str] = None
	parentPath: Optional[str] = None
	points: List[PPoint] = dataclasses.field(default_factory=list)
	closed: Optional[bool] = None
	color: Optional[tdu.Color] = None
	depthLayer: Optional[int] = None
	rotateAxis: Optional[float] = None
	center: Optional[tdu.Vector] = None

	def pointPositions(self):
		return [point.pos for point in self.points] if self.points else []

	def centerOrAverage(self):
		return self.center or common.averageTduVectors(self.pointPositions())

	def isTriangle(self):
		return len(self.points) == 3 and self.closed

@dataclass
class PGroup(DataObject):
	groupName: str
	groupPath: Optional[str] = None
	shapeIndices: List[int] = dataclasses.field(default_factory=list)
	meta: Dict[str, Any] = dataclasses.field(default_factory=dict)

	def __post_init__(self):
		self.shapeIndices = self.shapeIndices or []

@dataclass
class PSequenceStep(DataObject):
	sequenceIndex: int = 0
	shapeIndices: List[int] = dataclasses.field(default_factory=list)
	meta: Dict[str, Any] = dataclasses.field(default_factory=dict)

	def __post_init__(self):
		self.shapeIndices = self.shapeIndices or []

@dataclass
class PSequence(DataObject):
	sequenceName: str = None
	steps: List[PSequenceStep] = dataclasses.field(default_factory=list)
	meta: Dict[str, Any] = dataclasses.field(default_factory=dict)

	def __post_init__(self):
		self.steps = self.steps or []

@dataclass
class PPattern(DataObject):
	width: Optional[float] = None
	height: Optional[float] = None
	scale: Optional[float] = None
	offset: Optional[tdu.Vector] = None
	shapes: List[PShape] = dataclasses.field(default_factory=list)
	paths: List[PShape] = dataclasses.field(default_factory=list)
	groups: List[PGroup] = dataclasses.field(default_factory=list)
	sequences: List[PSequence] = dataclasses.field(default_factory=list)

	def __post_init__(self):
		self.shapes = self.shapes or []
		self.paths = self.paths or []
		self.groups = self.groups or []
		self.sequences = self.sequences or []
