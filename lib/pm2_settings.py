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

class ShapeSourceAttr(Enum):
	rgb = 'rgb'
	value = 'value'

@dataclass
class PScope(DataObject):
	groups: List[str] = dataclasses.field(default_factory=list)

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
class PGroupGenAttrs(DataObject):
	temporary: Optional[bool] = None
	mergeAs: Optional[str] = None

@dataclass
class PGroupGenSpec(DataObject):
	baseName: Optional[str] = None
	suffixes: List[str] = None
	attrs: Optional[PGroupGenAttrs] = None

@dataclass
class PPathGroupGenSpec(PGroupGenSpec):
	paths: List[str] = dataclasses.field(default_factory=list)
	groupAtPathDepth: Optional[int] = None

@dataclass
class PIdGroupGenSpec(PGroupGenSpec):
	ids: List[str] = dataclasses.field(default_factory=list)

@dataclass
class PGroupingSettings(DataObject):
	groupGenerators: List[PGroupGenSpec] = dataclasses.field(
		default_factory=list,
		metadata={
			'TypeMap': TypeMap(
				path=PPathGroupGenSpec,
				id=PIdGroupGenSpec,
			)
		}
	)

@dataclass
class PSequenceGenAttrs(DataObject):
	temporary: Optional[bool] = None

@dataclass
class PSequenceGenSpec(DataObject):
	sequenceName: Optional[str] = None
	suffixes: List[str] = None
	attrs: Optional[PSequenceGenAttrs] = None
	scopes: List[PScope] = dataclasses.field(default_factory=list)

@dataclass
class PAttrSequenceGenSpec(PSequenceGenSpec):
	byAttr: Optional[ShapeSourceAttr] = None
	roundDigits: Optional[int] = None
	reverse: Optional[bool] = None

@dataclass
class PPathSequenceGenSpec(PSequenceGenSpec):
	pathPath: Optional[str] = None

@dataclass
class PSequencingSettings(DataObject):
	sequenceGenerators: List[PSequenceGenSpec] = dataclasses.field(
		default_factory=list,
		metadata={
			'TypeMap': TypeMap(
				attr=PAttrSequenceGenSpec,
				path=PPathSequenceGenSpec,
			)
		}
	)

@dataclass
class PDuplicateMergeSettings(DataObject):
	tolerance: Optional[float] = None
	equivalence: Optional[ShapeEquivalence] = None
	scopes: List[PScope] = dataclasses.field(default_factory=list)
	ignoreDepth: Optional[bool] = None

@dataclass
class PSettings(DataObject):
	preProc: Optional[PPreProcSettings] = None
	grouping: Optional[PGroupingSettings] = None
	sequencing: Optional[PSequencingSettings] = None
	dedup: Optional[PDuplicateMergeSettings] = None
