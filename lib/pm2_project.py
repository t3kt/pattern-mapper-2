from dataclasses import dataclass, field
from typing import Optional, List

from common import DataObject, TypeMap
from pm2_state import PShapeState

@dataclass
class PShapeStateGenSpec(DataObject):
	enable: Optional[bool] = False
	amount: Optional[float] = None

@dataclass
class POverrideShapeStateSpec(PShapeStateGenSpec):
	groupName: Optional[str] = None
	shapeState: Optional[PShapeState] = None
	invertMask: Optional[bool] = None

@dataclass
class PRenderSettings(DataObject):
	useCustomRes: Optional[bool] = None
	renderWidth: Optional[int] = None
	renderHeight: Optional[int] = None
	wireEnable: Optional[bool] = None
	fillEnable: Optional[bool] = None

@dataclass
class PProject(DataObject):
	stateGenerators: List[PShapeStateGenSpec] = field(
		default_factory=list,
		metadata={
			'TypeMap': TypeMap(
				override=POverrideShapeStateSpec,
			)
		})
	render: Optional[PRenderSettings] = None
