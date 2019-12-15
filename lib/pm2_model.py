import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from common import DataObject, cleanDict, mergeDicts, excludeKeys
from common import CoordT, ColorT

# import td_python_package_init
# td_python_package_init.init()
#
# from dataclasses_serialization.json import JSONSerializer


@dataclass
class PPoint(DataObject):
	pos: CoordT

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
