import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from common import DataObject, TypeMap

class BoundType(Enum):
	frame = 'frame'
	shapes = 'shapes'

@dataclass
class PRecenterSettings(DataObject):
	centerOnShape: Optional[str] = None
	boundType: Optional[BoundType] = None

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
	temporary: Optional[bool] = None

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
				PPathGroupGenSpec,
			)
		}
	)

@dataclass
class PSettings(DataObject):
	preProc: Optional[PPreProcSettings] = None
	grouping: Optional[PGroupingSettings] = None
