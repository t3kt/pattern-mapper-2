from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from common import DataObject
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
	wireWidth: Optional[float] = None
	textures: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PComponentSpec(DataObject):
	compType: Optional[str] = None
	name: Optional[str] = None
	pars: Dict[str, Any] = field(default_factory=dict)
	subCompPars: Dict[str, Dict[str, Any]] = field(default_factory=dict)

@dataclass
class PSourcesSettings(DataObject):
	sources: List[PComponentSpec] = field(default_factory=list)

@dataclass
class PStateGenSettings(DataObject):
	generators: List[PComponentSpec] = field(default_factory=list)
	filterPars: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PProject(DataObject):
	state: Optional[PStateGenSettings] = None
	sources: Optional[PSourcesSettings] = None
	render: Optional[PRenderSettings] = None
