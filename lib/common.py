import typing
from typing import Callable, Dict, Iterable, List, Optional
import dataclasses
from enum import Enum

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

import td_python_package_init

td_python_package_init.init()

import typing_inspect

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

def _valToJson(val):
	# this must be done before the == '' and other comparisons since these
	# classes throw exceptions when compared against non-supported values.
	if isinstance(val, (tdu.Vector, tdu.Color)):
		return list(val)
	if val is None or val == '':
		return None
	if dataclasses.is_dataclass(val) and hasattr(val, 'toJsonDict'):
		return val.toJsonDict()
	if isinstance(val, Enum):
		return val.name
	if isinstance(val, str):
		return val
	if isinstance(val, (list, tuple)):
		return [_valToJson(v) for v in val]
	if isinstance(val, dict):
		return {k: _valToJson(v) for k, v in val.items()}
	return val

def _valFromJson(jVal, valType: type):
	# print('_valFromJson({}, valType: {!r})'.format(repr(jVal)[:30], valType))
	if jVal is None:
		return None
	if typing_inspect.is_optional_type(valType):
		return _valFromJson(jVal, typing_inspect.get_args(valType)[0])
	try:
		if valType is tdu.Vector:
			return tdu.Vector(jVal[0], jVal[1], jVal[2] if len(jVal) > 2 else 0)
		if valType is tdu.Color:
			return tdu.Color(
				jVal[0], jVal[1], jVal[2],
				jVal[3] if len(jVal) > 3 else 1)
		if isinstance(valType, type) and issubclass(valType, Enum):
			# noinspection PyTypeChecker
			return _enumByName(valType, jVal)
		valTypeOrigin = typing_inspect.get_origin(valType)
		if valTypeOrigin in (list, tuple):
			if not jVal:
				vals = []
			else:
				typeArg = typing_inspect.get_args(valType)[0]
				vals = [_valFromJson(v, typeArg) for v in jVal]
			return valTypeOrigin(vals)
		if valTypeOrigin is dict:
			if not jVal:
				return {}
			vType = typing_inspect.get_args(valType)[1]
			return {
				k: _valFromJson(v, vType)
				for k, v in jVal.items()
			}
		if dataclasses.is_dataclass(valType) and hasattr(valType, 'fromJsonDict'):
			return valType.fromJsonDict(jVal)
		return valType(jVal)
	except TypeError as e:
		dbgVal = repr(jVal)
		if len(dbgVal) > 30:
			dbgVal = dbgVal[:29] + '...'
		raise TypeError('Error handling field with valType: {!r} and value: {}: {}'.format(valType, dbgVal, e))

@dataclasses.dataclass
class DataObject:
	# def toJsonDict(self):
	# 	return cleanDict(JSONSerializer.serialize(self))
	#
	# @classmethod
	# def fromJsonDict(cls, obj):
	# 	return JSONSerializer.deserialize(cls, obj)

	def toJsonDict(self) -> dict:
		obj = {
			k: _valToJson(v)
			for k, v in dataclasses.asdict(self).items()
		}
		return cleanDict(obj)

	@classmethod
	def fromJsonDict(cls, obj):
		fieldVals = {
			f.name: _valFromJson(obj.get(f.name), f.type)
			for f in dataclasses.fields(cls)
		}
		# noinspection PyArgumentList
		return cls(**fieldVals)

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

def _enumByName(cls: typing.Type[Enum], name: str, default: Enum = None):
	if name is None or name == '':
		return default
	try:
		return cls[name]
	except KeyError:
		return default

def aggregateTduVectors(vecs: Iterable[tdu.Vector], aggregate=Callable[[Iterable[float]], float]):
	vecs = list(vecs)  # avoid duplicating lazily produced inputs
	return tdu.Vector(
		aggregate(v.x for v in vecs),
		aggregate(v.y for v in vecs),
		aggregate(v.z for v in vecs),
	)

def averageTduVectors(vecs: Iterable[tdu.Vector]):
	return aggregateTduVectors(vecs, average)

def average(vals):
	vals = list(vals)
	return sum(vals) / len(vals)

