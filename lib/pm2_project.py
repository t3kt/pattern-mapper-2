from dataclasses import dataclass, field
from typing import Optional, List

from common import DataObject
from pm2_state import PShapeState

@dataclass
class PGroupShapeState(PShapeState):
	groupName: str = None

@dataclass
class PProject(DataObject):
	defaultShapeState: Optional[PShapeState] = None
	groupShapeStates: List[PGroupShapeState] = field(default_factory=list)
