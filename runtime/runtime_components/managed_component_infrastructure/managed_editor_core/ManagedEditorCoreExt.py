from typing import Optional, List, Dict, Any

from common import ExtensionBase
from pm2_managed_components import ManagedComponentEditorInterface, ManagedComponentState
from pm2_messaging import CommonMessages, MessageHandler, Message
from pm2_project import PComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ManagedEditorCore(ExtensionBase, ManagedComponentEditorInterface):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.paramMap = {}  # type: Dict[str, Par]

	def InitializeEditor(self, spec: PComponentSpec):
		self.par.Targetname = spec.name
		pass

	def SetParVal(self, name: str, val):
		pass

	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(
			name,
			data,
			namespace=namespace or str(self.par.Messagenamespace)))
