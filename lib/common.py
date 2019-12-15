from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union
import dataclasses

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


class LoggableBase:
	def _GetLogId(self) -> Optional[str]:
		return None

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		raise NotImplementedError()

	def _LogBegin(self, event):
		self._LogEvent(event, indentafter=True)

	def _LogEnd(self, event=None):
		self._LogEvent(event, unindentbefore=True)


class ExtensionBase(LoggableBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: OP
		self.enablelogging = True
		self.par = ownerComp.par
		self.path = ownerComp.path
		self.op = ownerComp.op
		self.ops = ownerComp.ops
		# noinspection PyUnreachableCode
		if False:
			self.storage = {}
			self.docked = []
			self.destroy = ownerComp.destroy

	def _GetLogId(self):
		if not self.ownerComp.valid or not hasattr(self.ownerComp.par, 'opshortcut'):
			return None
		return self.ownerComp.par.opshortcut.eval()

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		pass


class LoggableSubComponent(LoggableBase):
	def __init__(self, hostobj: LoggableBase, logprefix: str = None):
		self.hostobj = hostobj
		self.logprefix = logprefix if logprefix is not None else type(self).__name__

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		if self.hostobj is None:
			return
		if self.logprefix and event:
			event = self.logprefix + ' ' + event
		self.hostobj._LogEvent(event, indentafter=indentafter, unindentbefore=unindentbefore)

def cleanDict(d):
	if not d:
		return None
	return {
		key: val
		for key, val in d.items()
		if not (val is None or (isinstance(val, (str, list, dict, tuple)) and len(val) == 0))
	}

def mergeDicts(*parts):
	x = {}
	for part in parts:
		if part:
			x.update(part)
	return x

def excludeKeys(d, keys):
	if not d:
		return {}
	return {
		key: val
		for key, val in d.items()
		if key not in keys
	}

@dataclasses.dataclass
class DataObject:
	# def toJsonDict(self):
	# 	return cleanDict(JSONSerializer.serialize(self))
	#
	# @classmethod
	# def fromJsonDict(cls, obj):
	# 	return JSONSerializer.deserialize(cls, obj)

	def toJsonDict(self) -> dict:
		return cleanDict(dataclasses.asdict(self))

	@classmethod
	def fromJsonDict(cls, obj):
		return cls(**obj)

	@classmethod
	def fromJsonDicts(cls, objs: List[Dict]):
		return [cls.fromJsonDict(obj) for obj in objs] if objs else []

	@classmethod
	def fromOptionalJsonDict(cls, obj, default=None):
		return cls.fromJsonDict(obj) if obj else default

	@classmethod
	def toJsonDicts(cls, nodes: 'Iterable[DataObject]'):
		return [n.toJsonDict() for n in nodes] if nodes else []

	@classmethod
	def toOptionalJsonDict(cls, obj: 'DataObject'):
		return obj.toJsonDict() if obj is not None else None


Vec2T = Tuple[float, float]
Vec3T = Tuple[float, float, float]
Vec4T = Tuple[float, float, float, float]
CoordT = Union[Vec2T, Vec3T]
ColorT = Union[Vec3T, Vec4T]

def aggregateTduVectors(vecs: Iterable[tdu.Vector], aggregate=Callable[[Iterable[float]], float]):
	vecs = list(vecs)  # avoid duplicating lazily produced inputs
	return tdu.Vector(
		aggregate(v.x for v in vecs),
		aggregate(v.y for v in vecs),
		aggregate(v.z for v in vecs),
	)
