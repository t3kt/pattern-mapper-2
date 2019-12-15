import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from common import DataObject
from common import CoordT, ColorT
import common

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def _createTduVector(coord: CoordT):
	return tdu.Vector(
		coord[0],
		coord[1],
		coord[2] if len(coord) > 2 else 0,
	)

@dataclass
class PPoint(DataObject):
	pos: CoordT

	def posVector(self):
		return _createTduVector(self.pos)

	def setPosVector(self, val: tdu.Vector):
		self.pos = tuple(val)

	def offsetPos(self, offset: tdu.Vector):
		self.setPosVector(self.posVector() + offset)

@dataclass
class PShape(DataObject):
	shapeIndex: Optional[int] = None
	shapeName: Optional[str] = None
	path: Optional[str] = None
	parentPath: Optional[str] = None
	points: List[PPoint] = dataclasses.field(default_factory=list)
	color: Optional[ColorT] = None
	depthLayer: Optional[int] = None
	rotateAxis: Optional[float] = None
	center: Optional[CoordT] = None

	def pointPosVectors(self):
		return [point.posVector() for point in self.points] if self.points else []

	def centerVector(self):
		if self.center:
			return _createTduVector(self.center)
		return common.averageTduVectors(self.pointPosVectors())

	def offsetPoints(self, offset: tdu.Vector):
		for point in self.points:
			point.offsetPos(offset)
		if self.center:
			self.center = tuple(self.centerVector() + offset)

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
	shapes: List[PShape] = dataclasses.field(default_factory=list)
	paths: List[PShape] = dataclasses.field(default_factory=list)
	groups: List[PGroup] = dataclasses.field(default_factory=list)
