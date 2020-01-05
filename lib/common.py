import datetime
import typing
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union
import dataclasses
from dataclasses import dataclass, field
from enum import Enum
import json
import sys

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

import td_python_package_init

td_python_package_init.init()

import typing_inspect


_TimestampFormat = '[%H:%M:%S]'
_PreciseTimestampFormat = '[%H:%M:%S.%f]'

def _LoggerTimestamp():
	return datetime.datetime.now().strftime(
		# _TimestampFormat
		_PreciseTimestampFormat
	)

def Log(msg, file=None):
	print(
		_LoggerTimestamp(),
		msg,
		file=file)
	if file:
		file.flush()

class IndentedLogger:
	def __init__(self, outfile=None):
		self._indentLevel = 0
		self._indentStr = ''
		self._outFile = outfile

	def _AddIndent(self, amount):
		self._indentLevel += amount
		self._indentStr = '\t' * self._indentLevel

	def Indent(self):
		self._AddIndent(1)

	def Unindent(self):
		self._AddIndent(-1)

	def LogEvent(self, path, opid, event, indentafter=False, unindentbefore=False):
		if unindentbefore:
			self.Unindent()
		if event:
			if not path and not opid:
				Log('%s%s' % (self._indentStr, event), file=self._outFile)
			elif not opid:
				Log('%s%s %s' % (self._indentStr, path or '', event), file=self._outFile)
			else:
				Log('%s[%s] %s %s' % (self._indentStr, opid or '', path or '', event), file=self._outFile)
		if indentafter:
			self.Indent()

	def LogBegin(self, path, opid, event):
		self.LogEvent(path, opid, event, indentafter=True)

	def LogEnd(self, path, opid, event):
		self.LogEvent(path, opid, event, unindentbefore=True)

class _Tee:
	def __init__(self, *files):
		self.files = files

	def write(self, obj):
		for f in self.files:
			f.write(obj)
			# f.flush()  # make the output to be visible immediately

	def flush(self):
		for f in self.files:
			f.flush()

def _InitFileLog():
	f = open(project.name + '-log.txt', mode='a')
	print('\n-----[Initialize Log: {}]-----\n'.format(
		datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f')), file=f)
	f.flush()
	return IndentedLogger(outfile=_Tee(sys.stdout, f))

_logger = IndentedLogger()
# _logger = _InitFileLog()

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

	def pars(self, *pattern: str) -> List[Par]:
		return self.ownerComp.pars(*pattern)

	def _GetLogId(self):
		if not self.ownerComp.valid or not hasattr(self.ownerComp.par, 'opshortcut'):
			return None
		return self.ownerComp.par.opshortcut.eval()

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		if self.enablelogging:
			_logger.LogEvent(
				self.ownerComp.path,
				self._GetLogId(),
				event,
				indentafter=indentafter,
				unindentbefore=unindentbefore)


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

def _defaultformatargs(args, kwargs):
	if not args:
		return kwargs or ''
	if not kwargs:
		return args
	return '{} {}'.format(args, kwargs)

def _decoratewithlogging(func, formatargs):
	def wrapper(self: ExtensionBase, *args, **kwargs):
		self._LogBegin('{}({})'.format(func.__name__, formatargs(args, kwargs)))
		try:
			return func(self, *args, **kwargs)
		finally:
			self._LogEnd()
	return wrapper

def loggedmethod(func):
	return _decoratewithlogging(func, _defaultformatargs)

def simpleloggedmethod(func):
	return customloggedmethod(omitargs=True)(func)

def customloggedmethod(
		omitargs: Union[bool, List[str]] = None):
	if not omitargs:
		formatargs = _defaultformatargs
	elif omitargs is True:
		def formatargs(*_):
			return ''
	elif not isinstance(omitargs, (list, tuple, set)):
		raise Exception('Invalid "omitargs" specifier for loggedmethod: {!r}'.format(omitargs))
	else:
		def formatargs(args, kwargs):
			return _defaultformatargs(args, excludeKeys(kwargs, omitargs))

	return lambda func: _decoratewithlogging(func, formatargs)

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

class TypeMap:
	def __init__(self, **typesByCode):
		self.typesByCode = typesByCode
		self.codesByType = {t: c for c, t in typesByCode.items()}
	def getCodeForType(self, t: type) -> str: return self.codesByType.get(t)
	def getTypeFromCode(self, code: str) -> type: return self.typesByCode.get(code)

def _valToJson(val, field: dataclasses.Field):
	# this must be done before the == '' and other comparisons since these
	# classes throw exceptions when compared against non-supported values.
	if isinstance(val, (tdu.Vector, tdu.Position, tdu.Color)):
		return list(val)
	if val is None or val == '':
		return None
	if dataclasses.is_dataclass(val) and hasattr(val, 'toJsonDict'):
		obj = val.toJsonDict()
		typeMap = field.metadata.get('TypeMap') if field else None  # type: TypeMap
		code = typeMap.getCodeForType(type(val)) if typeMap else None
		if code:
			obj['_t'] = code
		return obj
	if isinstance(val, Enum):
		return val.name
	if isinstance(val, str):
		return val
	if isinstance(val, (list, tuple)):
		return [_valToJson(v, field) for v in val]
	if isinstance(val, dict):
		return {k: _valToJson(v, field) for k, v in val.items()}
	return val

# def _unwrapForwardTypeRef(t):
# 	if isinstance(t, typing.Fo)

def _valFromJson(jVal, valType: type, field: dataclasses.Field):
	# print('_valFromJson({}, valType: {!r})'.format(repr(jVal)[:30], valType))
	if jVal is None:
		return None
	if typing_inspect.is_optional_type(valType):
		return _valFromJson(jVal, typing_inspect.get_args(valType)[0], field)
	try:
		if valType is tdu.Vector:
			return tdu.Vector(jVal[0], jVal[1], jVal[2] if len(jVal) > 2 else 0)
		if valType is tdu.Position:
			return tdu.Position(jVal[0], jVal[1], jVal[2] if len(jVal) > 2 else 0)
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
				vals = [_valFromJson(v, typeArg, field) for v in jVal]
			return valTypeOrigin(vals)
		if valTypeOrigin is dict:
			if not jVal:
				return {}
			vType = typing_inspect.get_args(valType)[1]
			return {
				k: _valFromJson(v, vType, field)
				for k, v in jVal.items()
			}
		if dataclasses.is_dataclass(valType) and hasattr(valType, 'fromJsonDict'):
			if '_t' in jVal:
				typeMap = field.metadata.get('TypeMap') if field else None  # type: TypeMap
				if typeMap:
					valType = typeMap.getTypeFromCode(jVal['_t']) or valType
			return valType.fromJsonDict(jVal)
		return valType(jVal)
	except TypeError as e:
		dbgVal = repr(jVal)
		if len(dbgVal) > 30:
			dbgVal = dbgVal[:29] + '...'
		raise TypeError('Error handling field with valType: {!r} and value: {}: {}'.format(valType, dbgVal, e))

def _isEmptyList(val):
	if isinstance(val, (list, tuple)) and len(val) == 0:
		return True
	return False

def parMeta(*parNames: str, switchPar: str = None):
	return {'Param': tuple(parNames), 'Switch': switchPar}

def subObjMeta(prefix: str):
	return {'ParamPrefix': prefix}

@dataclasses.dataclass
class DataObject:
	def toJsonDict(self) -> dict:
		obj = {}
		for field in dataclasses.fields(self):
			val = _valToJson(getattr(self, field.name), field)
			if val is None or _isEmptyList(val):
				continue
			obj[field.name] = val
		return obj

	@classmethod
	def fromJsonDict(cls, obj):
		fieldVals = {
			f.name: _valFromJson(obj.get(f.name), f.type, f)
			for f in dataclasses.fields(cls)
		}
		# noinspection PyArgumentList
		return cls(**fieldVals)

	# def toParamDict(self, prefix: str = None, includeSwitches=False):
	# 	switches = {}
	# 	params = {}
	# 	for field in dataclasses.fields(self):
	# 		pass
	# 	pass
	#
	# def toParamSwitches(self, prefix: str = None):
	# 	prefix = prefix.lower() if prefix else ''
	#
	# 	pass

	def isEmpty(self):
		# TODO: optimize this
		return not self.toJsonDict()

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

	@classmethod
	def parseJsonStr(cls, jsonStr: str):
		return cls.fromJsonDict(_parseJson(jsonStr))

	def toJsonStr(self, minify=True):
		return _toJson(self.toJsonDict(), minify=minify)

def _parseJson(jsonStr: str):
	return json.loads(jsonStr) if jsonStr else {}

def _toJson(obj, minify=True):
	return '{}' if not obj else json.dumps(
		obj,
		indent=None if minify else '  ',
		separators=(',', ':') if minify else (',', ': '),
		sort_keys=True,
	)

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

def formatValue(val):
	if isinstance(val, str):
		return val
	if val is None:
		return ''
	if isinstance(val, bool):
		return str(int(val))
	if isinstance(val, float) and int(val) == val:
		return str(int(val))
	return str(val)


def formatValueList(vals):
	return ' '.join([formatValue(i) for i in vals]) if vals else ''

def parseValue(val, nonevalue=''):
	if val is None or val == nonevalue:
		return None
	if val == '' or isinstance(val, (int, float)):
		return val
	try:
		# noinspection PyTypeChecker
		parsed = float(val)
		if int(parsed) == parsed:
			return int(parsed)
		return parsed
	except ValueError:
		return val

def longestCommonPrefix(strs):
	if not strs:
		return []
	for i, letter_group in enumerate(zip(*strs)):
		if len(set(letter_group)) > 1:
			return strs[0][:i]
	else:
		return min(strs)

class ValueSequence:
	def __init__(self, vals, cyclic, backup=None):
		self.vals = list(vals or [])
		self.cyclic = cyclic
		self.backup = backup

	@classmethod
	def FromSpec(cls, spec, parse=None, cyclic=True, backup=None):
		if spec in (None, ''):
			vals = []
		elif isinstance(spec, str):
			vals = spec.split()
		elif isinstance(spec, (list, tuple)):
			vals = spec
		else:
			vals = [spec]
		if parse is None:
			parse = parseValue
		return cls(map(parse, vals), cyclic=cyclic, backup=backup)

	def __len__(self): return len(self.vals)
	def __iter__(self): return iter(self.vals)
	def __bool__(self): return bool(self.vals)

	def __getitem__(self, index):
		if not self.vals:
			return None
		if 0 <= index < len(self.vals):
			return self.vals[index]
		if self.cyclic:
			return self.vals[index % len(self.vals)]
		elif callable(self.backup):
			return self.backup(index)
		else:
			return self.backup

	def permuteWith(self, otherseq: 'ValueSequence', n=None):
		if n is None:
			n = max(len(self), len(otherseq))
		for i in range(n):
			yield self[i], otherseq[i]

	def __str__(self):
		return '({})'.format(' '.join(map(str, self.vals)))

	def __repr__(self):
		return '{}(vals={!r}, cyclic={!r})'.format(
			type(self).__name__, self.vals, self.cyclic)

def _padTo4(val: Union[str, float, int, bool, Iterable[Union[str, float, int, bool]]]):
	if isinstance(val, str):
		val = [val]
	if not isinstance(val, (list, tuple)):
		val = [val]
	return [val[i if i < len(val) else -1] for i in range(4)]

def configurePar(
		par: Union['Par', Iterable['Par']],
		default: Union[Union[str, float, bool], Iterable[Union[str, float, bool]]] = None,
		normMin: Union[float, Iterable[float]] = None,
		normMax: Union[float, Iterable[float]] = None,
		clampMin: Union[float, Iterable[float]] = None,
		clampMax: Union[float, Iterable[float]] = None,
):
	if not isinstance(par, (list, tuple)):
		par = [par]
	default = _padTo4(default)
	normMin = _padTo4(normMin)
	normMax = _padTo4(normMax)
	clampMin = _padTo4(clampMin)
	clampMax = _padTo4(clampMax)
	for i, p in enumerate(par):
		if default[i] is not None:
			p.default = default[i]
			p.val = default[i]
		if normMin[i] is not None:
			p.normMin = normMin[i]
		if normMax[i] is not None:
			p.normMax = normMax[i]
		if clampMin[i] is not None:
			p.min = clampMin[i]
			p.clampMin = True
		if clampMax[i] is not None:
			p.max = clampMax[i]
			p.clampMax = True

@dataclass
class OPAttrs:
	order: Optional[float] = None
	nodePos: Optional[Tuple[float, float]] = None
	tags: Optional[List[str]] = None
	panelParent: Optional['COMP'] = None
	parVals: Optional[Dict[str, Any]] = None
	parExprs: Optional[Dict[str, str]] = None
	inputs: Optional[List] = None  # TODO: use a more specific type parameter

	def overrideWith(self, other: 'OPAttrs') -> 'OPAttrs':
		if not other:
			return self
		if other.order is not None:
			self.order = other.order
		self.nodePos = other.nodePos or self.nodePos
		if other.tags:
			if self.tags is not None:
				self.tags += other.tags
			else:
				self.tags = list(other.tags)
		self.panelParent = other.panelParent or self.panelParent
		if other.parVals:
			if self.parVals is not None:
				self.parVals.update(other.parVals)
			else:
				self.parVals = dict(other.parVals)
		if other.parExprs:
			if self.parExprs is not None:
				self.parExprs.update(other.parExprs)
			else:
				self.parExprs = dict(other.parExprs)
		if other.inputs is not None:
			self.inputs = list(other.inputs)
		return self

	def applyTo(self, o: 'OP'):
		if self.order is not None:
			o.par.alignorder = self.order
		if self.nodePos:
			o.nodeCenterX, o.nodeCenterY = self.nodePos
		if self.tags:
			o.tags.update(self.tags)
		if self.panelParent:
			self.panelParent.outputCOMPConnectors[0].connect(o)
		if self.parVals:
			for key, val in self.parVals.items():
				setattr(o.par, key, val)
		if self.parExprs:
			for key, val in self.parExprs.items():
				getattr(o.par, key).expr = val
		if self.inputs:
			for i, source in enumerate(self.inputs):
				o.inputConnectors[i].connect(source)

	@classmethod
	def merged(cls, *attrs: 'OPAttrs'):
		result = cls()
		for a in attrs:
			result.overrideWith(a)
		return result

def createFromTemplate(
		template: 'OP',
		dest: 'COMP',
		name: str,
		attrs: OPAttrs = None):
	comp = dest.copy(template, name=name)
	if attrs:
		attrs.applyTo(comp)
	return comp
