import dataclasses
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Union

# import td_python_package_init
# td_python_package_init.init()
#
# from dataclasses_serialization.json import JSONSerializer

_Vec2 = Tuple[float, float]
_Vec3 = Tuple[float, float, float]
_Vec4 = Tuple[float, float, float, float]
_Coord = Union[_Vec2, _Vec3]
_Color = Union[_Vec3, _Vec4]

def _cleanDict(d):
	if not d:
		return None
	return {
		key: val
		for key, val in d.items()
		if not (val is None or (isinstance(val, (str, list, dict, tuple)) and len(val) == 0))
	}

def _mergeDicts(*parts):
	x = {}
	for part in parts:
		if part:
			x.update(part)
	return x

def _excludeKeys(d, keys):
	if not d:
		return {}
	return {
		key: val
		for key, val in d.items()
		if key not in keys
	}

@dataclass
class DataObject:
	# def toJsonDict(self):
	# 	return _cleanDict(JSONSerializer.serialize(self))
	#
	# @classmethod
	# def fromJsonDict(cls, obj):
	# 	return JSONSerializer.deserialize(cls, obj)

	def toJsonDict(self) -> dict:
		return _cleanDict(dataclasses.asdict(self))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(**obj)

	@classmethod
	def fromJsonDicts(cls, objs: List[Dict]):
		return [cls.fromJsonDict(obj) for obj in objs] if objs else []

	@classmethod
	def fromOptionalJsonDict(cls, obj, default=None):
		return cls.fromJsonDict(obj) if obj else default

	@classmethod
	def toJsonDicts(cls, nodes: 'Iterable[DataObject]'):
		return [n.toJsonDict() for n in nodes] if nodes else []

	@classmethod
	def toOptionalJsonDict(cls, obj: 'DataObject'):
		return obj.toJsonDict() if obj is not None else None

@dataclass
class PShape(DataObject):
	shapeIndex: Optional[int] = None
	name: Optional[str] = None
	path: Optional[str] = None
	parentPath: Optional[str] = None
	points: List['PPoint'] = dataclasses.field(default_factory=list)
	color: Optional[_Color] = None

	def toJsonDict(self) -> dict:
		return _cleanDict(_mergeDicts(
			_excludeKeys(super().toJsonDict(), ['points']),
			{'points': PPoint.toJsonDicts(self.points)},
		))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(
			points=PPoint.fromJsonDicts(obj.get('points')),
			**_excludeKeys(obj, ['points'])
		)

@dataclass
class PPoint(DataObject):
	pos: Optional[_Coord] = None


@dataclass
class PPattern(DataObject):
	shapes: List['PShape'] = dataclasses.field(default_factory=list)
	paths: List['PShape'] = dataclasses.field(default_factory=list)
	width: Optional[float] = None
	height: Optional[float] = None

	def toJsonDict(self) -> dict:
		return _cleanDict(_mergeDicts(
			_excludeKeys(super().toJsonDict(), ['shapes', 'paths']),
			{
				'shapes': PShape.toJsonDicts(self.shapes),
				'paths': PShape.toJsonDicts(self.paths),
			}
		))
