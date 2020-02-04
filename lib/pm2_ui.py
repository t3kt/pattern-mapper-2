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
	subType: str
	name: str

	@classmethod
	def getFromComp(cls, comp: 'OP') -> Optional['MarkerObject']:
		if not comp:
			return None
		if hasattr(comp.par, 'Markertype'):
			return MarkerObject(
				comp.par.Markertype.eval(),
				comp.par.Markersubtype.eval(),
				comp.par.Markerobjname.eval(),
			)
		if hasattr(comp.parent, 'marker'):
			return cls.getFromComp(comp.parent.marker)

class DropReceiver(ABC):
	def HandleDrop(
			self,
			dropName: str, dropExt: str,
			baseName: str, destPath: str) -> bool:
		if dropExt == 'COMP':
			parentComp = op(baseName)
			droppedComp = parentComp and parentComp.op(dropName)
			if droppedComp and self.HandleCOMPDrop(droppedComp, op(destPath)):
				return True
		return False

	def HandleCOMPDrop(self, droppedComp: 'COMP', dropTarget: 'COMP') -> bool:
		return False

class MarkerToParamReceiver(ExtensionBase, DropReceiver):
	def __init__(
			self,
			ownerComp,
			parName: str,
			supportedType: str,
			targetPath: str = None,
			append=False):
		super().__init__(ownerComp)
		self.parName = parName
		self.targetPath = targetPath
		self.supportedType = supportedType
		self.appendMode = append

	def HandleCOMPDrop(self, droppedComp: 'COMP', dropTarget: 'COMP') -> bool:
		markerObj = MarkerObject.getFromComp(droppedComp)
		if not markerObj:
			return False
		if markerObj.objectType != self.supportedType:
			self._LogEvent('WARNING: marker type not supported: {}'.format(markerObj))
			return False
		if self.targetPath:
			target = self.ownerComp.op(self.targetPath)
		else:
			target = self.ownerComp
		if not target:
			return False
		par = getattr(target.par, self.parName)
		if par is None:
			return False
		if self.appendMode and par:
			par.val = par.val + ' ' + markerObj.name
		else:
			par.val = markerObj.name
		return True

