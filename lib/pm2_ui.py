from abc import ABC
from typing import Any

from common import ExtensionBase
from pm2_messaging import MessageHandler, MessageSender, Message

# # noinspection PyUnreachableCode
# if False:
# 	# noinspection PyUnresolvedReferences
# 	from _stubs import *

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
