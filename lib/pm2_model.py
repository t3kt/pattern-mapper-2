from dataclasses import dataclass, field
from typing import List, Tuple, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_Vec2 = Tuple[float, float]
_Vec3 = Tuple[float, float, float]
_Vec4 = Tuple[float, float, float, float]
_Coord = Union[_Vec2, _Vec3]
_Color = Union[_Vec3, _Vec4]


@dataclass
class PShape:
	index: int = None
	name: str = None
	path: str = None
	parentPath: str = None
	points: List['PPoint'] = field(default_factory=list)
	color: _Color = None


@dataclass
class PPoint:
	pos: _Coord = None


@dataclass
class PPattern:
	shapes: List['PShape'] = field(default_factory=list)
	paths: List['PShape'] = field(default_factory=list)
	width: float = None
	height: float = None
