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
	color: Optional[tdu.Color] = None
	depthLayer: Optional[int] = None
	rotateAxis: Optional[float] = None
	center: Optional[tdu.Vector] = None

	def pointPositions(self):
		return [point.pos for point in self.points] if self.points else []

	def pointPositionsWithoutLoop(self):
		if self.isOpenLoop():
			return self.pointPositions()[:-1]
		return self.pointPositions()

	def centerOrAverage(self):
		return self.center or common.averageTduVectors(self.pointPositionsWithoutLoop())

	def isOpenLoop(self):
		return len(self.points) >= 4 and self.points[0].pos == self.points[-1].pos

	def isTriangle(self):
		if len(self.points) == 3 and not self.isOpenLoop():
			return True
		if len(self.points) == 4 and self.isOpenLoop():
			return True
		return False

@dataclass
class PGroup(DataObject):
	groupName: str
	groupPath: Optional[str] = None
	shapeIndices: List[int] = dataclasses.field(default_factory=list)
	meta: Dict[str, Any] = dataclasses.field(default_factory=dict)

@dataclass
class PPattern(DataObject):
	width: Optional[float] = None
	height: Optional[float] = None
	scale: Optional[float] = None
	offset: Optional[tdu.Vector] = None
	shapes: List[PShape] = dataclasses.field(default_factory=list)
	paths: List[PShape] = dataclasses.field(default_factory=list)
	groups: List[PGroup] = dataclasses.field(default_factory=list)

	def __post_init__(self):
		if self.shapes is None:
			self.shapes = []
		if self.paths is None:
			self.paths = []
		if self.groups is None:
			self.groups = []
