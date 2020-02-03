from abc import ABC
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
	name: str

class Marker(ExtensionBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self._InitParams()

	def _InitParams(self):
		if not hasattr(self.ownerComp.par, 'Markerobjtype'):
			page = self.ownerComp.appendCustomPage('Marker')
			page.appendStr('Markerobjtype', label=':Marker Type')
		if not hasattr(self.ownerComp.par, 'Markerobjname'):
			page = self.ownerComp.appendCustomPage('Marker')
			page.appendStr('Markerobjtype', label=':Marker Name')

	def GetMarkerObject(self) -> Optional[MarkerObject]:
		obj = MarkerObject(self.par.Markerobjtype.eval(), self.par.Markerobjname.eval())
		if obj.objectType and obj.name:
			return obj

def GetMarkerObjectFromOP(comp: 'OP') -> Optional[MarkerObject]:
	if hasattr(comp, 'GetMarkerObject'):
		return comp.GetMarkerObject()
	if hasattr(comp.ext, 'Marker'):
		return comp.ext.Marker.GetMarkerObject()
