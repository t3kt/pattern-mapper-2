from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from common import ExtensionBase
from pm2_messaging import MessageHandler, MessageSender, Message

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class UIApp(ExtensionBase, MessageHandler, MessageSender, ABC):
	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		if not self.par.Messagesendenable:
			return
		handler = self.ownerComp.parent.runtime  # type: MessageHandler
		handler.HandleMessage(Message(name, data, namespace))

class UIComponentBase(ExtensionBase):
	@property
	def UIApp(self) -> UIApp: return self.ownerComp.parent.ui

class UISubSystem(UIComponentBase, MessageHandler, MessageSender, ABC):
	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		if not self.par.Messagesendenable:
			return
		self.UIApp.SendMessage(
			name,
			data,
			namespace or str(self.par.Messagenamespace),
		)

@dataclass
class MarkerObject:
	objectType: str
	subType: str
	name: str

def GetMarkerObjectFromOP(comp: 'OP') -> Optional[MarkerObject]:
	if not comp:
		return None
	if hasattr(comp.par, 'Markertype'):
		return MarkerObject(
			comp.par.Markertype.eval(),
			comp.par.Markersubtype.eval(),
			comp.par.Markerobjname.eval(),
		)
	if hasattr(comp.parent, 'marker'):
		return GetMarkerObjectFromOP(comp.parent.marker)

class DropReceiver(ABC):
	@abstractmethod
	def HandleDrop(
			self,
			dropName: str, dropExt: str,
			baseName: str, destPath: str) -> bool:
		pass

class MarkerDropReceiver:
	pass
