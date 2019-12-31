from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from common import DataObject

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class UVMode(Enum):
	loc = 'loc'
	glob = 'glob'
	path = 'path'

@dataclass
class PTextureAttrs(DataObject):
	opacity: Optional[float] = None
	source: Optional[int] = None
	offset: Optional[tdu.Vector] = field(default=None, metadata={'Param': ('offsetx', 'offsety', 'offsetz')})
	scale: Optional[float] = None
	rotate: Optional[float] = None
	uvMode: Optional[UVMode] = None

@dataclass
class PAppearance(DataObject):
	opacity: Optional[float] = None
	color: Optional[tdu.Color] = field(default=None, metadata={'Param': ('colorr', 'colorg', 'colorb', 'colora')})
	texture: Optional[PTextureAttrs] = field(default=None, metadata={'Param': 'tex'})

@dataclass
class PTransform(DataObject):
	translate: Optional[tdu.Vector] = field(default=None, metadata={'Param': ('tx', 'ty', 'tz')})
	rotate: Optional[tdu.Vector] = field(default=None, metadata={'Param': ('rx', 'ry', 'rz')})
	scale: Optional[tdu.Vector] = field(default=None, metadata={'Param': ('sx', 'sy', 'sz')})
	pivot: Optional[tdu.Vector] = field(default=None, metadata={'Pivot': ('px', 'py', 'pz')})

@dataclass
class PShapeState:
	fill: Optional[PAppearance] = field(default=None, metadata={'Param': 'Fill'})
	wire: Optional[PAppearance] = field(default=None, metadata={'Param': 'Wire'})
	localTransform: Optional[PTransform] = field(default=None, metadata={'Param': 'Local'})
	globalTransform: Optional[PTransform] = field(default=None, metadata={'Param': 'Global'})

