from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Any

from common import DataObject

@dataclass
class Message(DataObject):
	name: str
	data: Any = None
	namespace: str = None

class CommonMessages:
	# Events
	added = 'added'
	deleted = 'deleted'
	renamed = 'renamed'
	cleared = 'cleared'
	parVal = 'parVal'
	parEnable = 'parEnable'
	parMode = 'parMode'

	# Actions
	add = 'add'
	delete = 'delete'
	rename = 'rename'
	clear = 'clear'
	setPar = 'setPar'
	queryParVals = 'queryParVals'
	# queryParStates = 'queryParStates'

class MessageNamespaces:
	stateGen = 'stateGen'
	source = 'source'
	control = 'control'

class MessageHandler(ABC):
	@abstractmethod
	def HandleMessage(self, message: Message):
		pass
