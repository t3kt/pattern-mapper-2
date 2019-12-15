import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional
from common import DataObject, cleanDict, mergeDicts, excludeKeys
from common import CoordT, ColorT

# import td_python_package_init
# td_python_package_init.init()
#
# from dataclasses_serialization.json import JSONSerializer

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class PPoint(DataObject):
	pos: CoordT

	def x(self): return self.pos[0]
	def y(self): return self.pos[1]
	def z(self): return self.pos[2] if len(self.pos) > 2 else 0

	def posVector(self):
		return tdu.Vector(self.x(), self.y(), self.z())

def _pointPosAggregate(points: Iterable[PPoint], aggregate=Callable[[Iterable[float]], float]):
	return tdu.Vector(
		aggregate(p.x() for p in points),
		aggregate(p.y() for p in points),
		aggregate(p.z() for p in points),
	)

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

	def toJsonDict(self) -> dict:
		return cleanDict(mergeDicts(
			excludeKeys(super().toJsonDict(), ['points']),
			{'points': PPoint.toJsonDicts(self.points)},
		))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(
			points=PPoint.fromJsonDicts(obj.get('points')),
			**excludeKeys(obj, ['points'])
		)

	def pointPosVectors(self):
		return [point.posVector() for point in self.points] if self.points else []

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

	def toJsonDict(self) -> dict:
		return cleanDict(mergeDicts(
			excludeKeys(super().toJsonDict(), ['shapes', 'paths', 'groups']),
			{
				'shapes': PShape.toJsonDicts(self.shapes),
				'paths': PShape.toJsonDicts(self.paths),
				'groups': PGroup.toJsonDicts(self.groups),
			}
		))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(
			shapes=PShape.fromJsonDicts(obj.get('shapes')),
			paths=PShape.fromJsonDicts(obj.get('paths')),
			groups=PGroup.fromJsonDicts(obj.get('groups')),
		)
