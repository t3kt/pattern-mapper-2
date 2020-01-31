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
	# Actions
	add = 'add'
	delete = 'delete'
	rename = 'rename'
	clear = 'clear'

class MessageHandler(ABC):
	@abstractmethod
	def HandleMessage(self, message: Message):
		pass
