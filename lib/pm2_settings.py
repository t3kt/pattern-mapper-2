from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from common import DataObject, cleanDict, mergeDicts, excludeKeys

@dataclass
class PPreProcSettings(DataObject):
	rescale: Optional[bool] = None
	recenter: Optional[bool] = None
	fixTriangleCenters: Optional[bool] = None

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
