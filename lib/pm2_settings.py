from dataclasses import dataclass
from enum import Enum
from typing import Optional
from common import DataObject

@dataclass
class PPreProcSettings(DataObject):
	recenter: Optional['PRecenterSettings'] = None
	rescale: Optional['PRescaleSettings'] = None
	fixTriangleCenters: Optional[bool] = None

@dataclass
class PRecenterSettings(DataObject):
	centerOnShape: Optional[str] = None
	boundType: Optional['BoundType'] = None

@dataclass
class PRescaleSettings(DataObject):
	bound: Optional['BoundType'] = None

class BoundType(Enum):
	frame = 'frame'
	shapes = 'shapes'

@dataclass
class PGroupingSettings(DataObject):
	pass

@dataclass
class PSettings(DataObject):
	preProc: Optional[PPreProcSettings] = None
	grouping: Optional[PGroupingSettings] = None
