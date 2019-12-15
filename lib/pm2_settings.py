from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from common import DataObject, cleanDict, mergeDicts, excludeKeys
import common

@dataclass
class PPreProcSettings(DataObject):
	recenter: Optional['PRecenterSettings'] = None
	rescale: Optional['PRescaleSettings'] = None
	fixTriangleCenters: Optional[bool] = None

	def toJsonDict(self) -> dict:
		return cleanDict(mergeDicts(
			super().toJsonDict(),
			{
				'recenter': PRecenterSettings.toOptionalJsonDict(self.recenter),
				'recsale': PRescaleSettings.toOptionalJsonDict(self.rescale),
			}
		))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(
			**excludeKeys(obj, ['recenter', 'rescale']),
			recenter=PRecenterSettings.fromOptionalJsonDict(obj.get('recenter')),
			rescale=PRescaleSettings.fromOptionalJsonDict(obj.get('rescale')),
		)

@dataclass
class PRecenterSettings(DataObject):
	centerOnShape: Optional[str] = None

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

	def toJsonDict(self) -> dict:
		return cleanDict({
			'preProc': PPreProcSettings.toOptionalJsonDict(self.preProc),
			'grouping': PGroupingSettings.toOptionalJsonDict(self.grouping),
		})

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(
			preProc=PPreProcSettings.fromOptionalJsonDict(obj.get('preProc')),
			grouping=PGroupingSettings.fromOptionalJsonDict(obj.get('grouping')),
		)
