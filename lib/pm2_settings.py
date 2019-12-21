import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from common import DataObject, TypeMap

class BoundType(Enum):
	frame = 'frame'
	shapes = 'shapes'

class BoolOp(Enum):
	OR = 'OR'
	AND = 'AND'

class ShapeEquivalence(Enum):
	# Compare the shape center positions and their radius
	centerRadius = 'centerRadius'

	# Are points equal, compared in the same order.
	alignedPoints = 'alignedPoints'

	# Are points equal, regardless of which point is the first point.
	# So shape1 (1,2) (3,4) (5,6)
	# equals shape2 (3,4) (5,6) (1,2)
	points = 'points'

@dataclass
class PRecenterSettings(DataObject):
	centerOnShape: Optional[str] = None
	bound: Optional[BoundType] = None

@dataclass
class PRescaleSettings(DataObject):
	bound: Optional[BoundType] = None

@dataclass
class PPreProcSettings(DataObject):
	recenter: Optional[PRecenterSettings] = None
	rescale: Optional[PRescaleSettings] = None
	fixTriangleCenters: Optional[bool] = None

@dataclass
class PGroupGenSpec(DataObject):
	groupName: Optional[str] = None
	suffixes: List[str] = None
	temporary: Optional[bool] = None
	mergeAs: Optional[str] = None

@dataclass
class PPathGroupGenSpec(PGroupGenSpec):
	paths: List[str] = dataclasses.field(default_factory=list)
	groupAtPathDepth: Optional[int] = None

@dataclass
class PGroupingSettings(DataObject):
	groupGenerators: List[PGroupGenSpec] = dataclasses.field(
		default_factory=list,
		metadata={
			'TypeMap': TypeMap(
				path=PPathGroupGenSpec,
			)
		}
	)

@dataclass
class PDuplicateMergeScope(DataObject):
	groups: List[str] = dataclasses.field(default_factory=list)

@dataclass
class PDuplicateMergeSettings(DataObject):
	tolerance: Optional[float] = None
	equivalence: Optional[ShapeEquivalence] = None
	scopes: List[PDuplicateMergeScope] = dataclasses.field(default_factory=list)
	ignoreDepth: Optional[bool] = None

@dataclass
class PSettings(DataObject):
	preProc: Optional[PPreProcSettings] = None
	grouping: Optional[PGroupingSettings] = None
	dedup: Optional[PDuplicateMergeSettings] = None
