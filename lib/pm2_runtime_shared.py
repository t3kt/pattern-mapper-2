from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Dict, Any, Union, Iterable, List

import common
from pm2_project import PProject, PShapeStateGenSpec, PComponentSpec
from pm2_state import PShapeState, PAppearance, PTextureAttrs, UVMode, PTransform

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.RuntimeAppExt import RuntimeApp

# @dataclass
# class _ParMapping:
# 	tupletName: str
# 	suffixes: str = None
# 	getter: Callable[[PShapeState], Any] = None
# 	setter: Callable[[PShapeState, Any], None] = None
#
#
# @dataclass
# class _ParGroup:
# 	pars: List[_ParMapping]
# 	switchName: str = None
#
#
#
#
# def _createShapeStateParMappings():
# 	groups = [
# 		_ParGroup(
# 			switchName='Includefillopacity',
# 			pars=[
# 				_ParMapping(
# 					'Fillopacity',
# 					getter=lambda state: state.fill.opacity,
# 					# setter=lambda state, val: state.fill = 8,
# 				)
# 			]
# 		)
# 	]
# 	pass

@dataclass
class _ParGroup:
	name: str
	label: str
	switchName: str
	parNames: List[str]

@dataclass
class _ParPage:
	name: str
	label: str
	parGroups: List[_ParGroup]

def _appearanceParPage(namePrefix: str, labelPrefix: str):
	pass

class ShapeStateExt(common.ExtensionBase):
	def SetShapeState(self, shapeState: PShapeState):
		shapeState = shapeState or PShapeState()
		self._SetAppearance(shapeState.fill, 'Fill')
		self._SetAppearance(shapeState.wire, 'Wire')
		self._SetTransform(shapeState.localTransform, 'Local')
		self._SetTransform(shapeState.globalTransform, 'Global')

	def GetShapeState(self):
		return PShapeState(
			fill=self._GetAppearance('Fill'),
			wire=self._GetAppearance('Wire'),
			localTransform=self._GetTransform('Local'),
			globalTransform=self._GetTransform('Global'),
		)

	def _GetAppearance(self, prefix: str):
		appearance = PAppearance()
		lowPrefix = prefix.lower()
		if getattr(self.par, 'Include' + lowPrefix + 'opacity'):
			appearance.opacity = float(getattr(self.par, prefix + 'opacity'))
		if getattr(self.par, 'Include' + lowPrefix + 'color'):
			appearance.color = tdu.Color(self.pars(prefix + 'color[rgba]'))
		texture = PTextureAttrs()
		if getattr(self.par, 'Include' + lowPrefix + 'tex'):
			texture.opacity = float(getattr(self.par, prefix + 'texopacity'))
			texture.source = int(getattr(self.par, prefix + 'texsource'))
			modeName = str(getattr(self.par, prefix + 'texuvmode'))
			if hasattr(UVMode, modeName):
				texture.uvMode = getattr(UVMode, modeName)
		if getattr(self.par, 'Include' + lowPrefix + 'textransform'):
			texture.offset = tdu.Vector(self.pars(prefix + 'texoffset[xyz]'))
			texture.rotate = float(getattr(self.par, prefix + 'texrotate'))
			texture.scale = float(getattr(self.par, prefix + 'texscale'))
		if not texture.isEmpty():
			appearance.texture = texture
		if appearance.isEmpty():
			return None
		return appearance

	def _GetTransform(self, prefix: str):
		transform = PTransform()
		lowPrefix = prefix.lower()
		if getattr(self.par, 'Include' + lowPrefix + 'translate'):
			transform.translate = tdu.Vector(self.pars(prefix + 't[xyz]'))
		if getattr(self.par, 'Include' + lowPrefix + 'rotate'):
			transform.rotate = tdu.Vector(self.pars(prefix + 'r[xyz]'))
		if getattr(self.par, 'Include' + lowPrefix + 'scale'):
			transform.scale = tdu.Vector(self.pars(prefix + 's[xyz]'))
		if getattr(self.par, 'Include' + lowPrefix + 'pivot'):
			transform.pivot = tdu.Vector(self.pars(prefix + 'p[xyz]'))
		if transform.isEmpty():
			return None
		return transform

	def _SetTransform(self, transform: PTransform, prefix: str):
		if not transform:
			transform = PTransform()
		setattr(self.par, 'Include' + prefix.lower() + 'translate', transform.translate is not None)
		val = transform.translate or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'tx', val.x)
		setattr(self.par, prefix + 'ty', val.y)
		setattr(self.par, prefix + 'tz', val.z)
		setattr(self.par, 'Include' + prefix.lower() + 'rotate', transform.rotate is not None)
		val = transform.rotate or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'rx', val.x)
		setattr(self.par, prefix + 'ry', val.y)
		setattr(self.par, prefix + 'rz', val.z)
		setattr(self.par, 'Include' + prefix.lower() + 'scale', transform.scale is not None)
		val = transform.scale or tdu.Vector(1, 1, 1)
		setattr(self.par, prefix + 'sx', val.x)
		setattr(self.par, prefix + 'sy', val.y)
		setattr(self.par, prefix + 'sz', val.z)
		setattr(self.par, 'Include' + prefix.lower() + 'pivot', transform.pivot is not None)
		val = transform.pivot or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'px', val.x)
		setattr(self.par, prefix + 'py', val.y)
		setattr(self.par, prefix + 'pz', val.z)

	def _SetAppearance(self, appearance: PAppearance, prefix: str):
		lowPrefix = prefix.lower()
		if not appearance:
			appearance = PAppearance()
		setattr(self.par, 'Include' + lowPrefix + 'opacity', appearance.opacity is not None)
		setattr(self.par, prefix + 'opacity', appearance.opacity if appearance.opacity is not None else 0)
		setattr(self.par, 'Include' + lowPrefix + 'color', appearance.color is not None)
		val = appearance.color or tdu.Color(1, 1, 1, 1)
		setattr(self.par, prefix + 'colorr', val.r)
		setattr(self.par, prefix + 'colorg', val.g)
		setattr(self.par, prefix + 'colorb', val.b)
		setattr(self.par, prefix + 'colora', val.a)
		texture = appearance.texture or PTextureAttrs()
		setattr(self.par, 'Include' + lowPrefix + 'tex', texture.opacity is not None or texture.source is not None or texture.uvMode is not None)
		setattr(self.par, prefix + 'texopacity', texture.opacity if texture.opacity is not None else 1)
		setattr(self.par, prefix + 'texsource', texture.source or 0)
		modePar = getattr(self.par, prefix + 'texuvmode')
		modePar.val = texture.uvMode.name if texture.uvMode is not None else modePar.default
		setattr(self.par, 'Include' + lowPrefix + 'textransform', texture.offset is not None or texture.rotate is not None or texture.scale is not None)
		val = texture.offset or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'texoffsetx', val.x)
		setattr(self.par, prefix + 'texoffsety', val.y)
		setattr(self.par, prefix + 'texoffsetz', val.z)
		setattr(self.par, prefix + 'texrotate', texture.rotate or 0)
		setattr(self.par, prefix + 'texscale', texture.scale if texture.scale is not None else 1)

def _appearanceAttrs(namePrefix: str, labelPrefix: str):
	attrs = dict(
		opacity='Opacity',
		colorr='Color Red',
		colorg='Color Green',
		colorb='Color Blue',
		colora='Color Alpha',
		texopacity='Texture Opacity',
		texsource='Texture Source',
		texuvmode='Texture UV Mode',
		texoffsetx='Texture Offset X',
		texoffsetY='Texture Offset Y',
		texoffsetz='Texture Offset Z',
		texrotate='Texture Rotate',
		texscalex='Texture Scale X',
		texscaley='Texture Scale Y',
		texscalez='Texture Scale Z',
	)
	return {
		namePrefix + name: labelPrefix + label
		for name, label in attrs.items()
	}
def _transformAttrs(namePrefix: str, labelPrefix: str):
	attrs = dict(
		tx='Translate X',
		tY='Translate Y',
		tz='Translate Z',
		rx='Rotate X',
		rY='Rotate Y',
		rz='Rotate Z',
		sx='Scale X',
		sY='Scale Y',
		sz='Scale Z',
		px='Pivot X',
		pY='Pivot Y',
		pz='Pivot Z',
	)
	return {
		namePrefix + name: labelPrefix + label
		for name, label in attrs.items()
	}

# ShapeStateChansMenuSource = common.createMenuSource(
# 	**common.mergeDicts(
# 		_appearanceAttrs('Fill', 'Fill '),
# 		_appearanceAttrs('Wire', 'Wire '),
# 		_transformAttrs('Local', 'Local '),
# 		_transformAttrs('Global', 'Global '),
# 	)
# )

# def ShapeAttrMenuSource(primary=True, definition=False, text=False):
# 	attrs = dict(
# 		shapeIndex='shapeIndex',
# 		shapeName='shapeName',
# 		path='path',
# 		parentPath='parentPath',
# 		closed='closed',
# 		point_count='point_count',
# 		color_r='color_r',
# 		color_g='color_g',
# 		color_b='color_b',
# 		color_a='color_a',
# 		center_x='center_x',
# 		center_y='center_y',
# 		center_z='center_z',
# 		depthLayer='depthLayer',
# 		rotateAxis='rotateAxis',
# 		isTriangle='isTriangle',
# 		pathLength='pathLength',
# 		dupCount='dupCount',
# 	)
# 	return common.mergeDicts(
# 		primary and dict(
#
# 		),
# 		definition and dict(
# 			shapeIndex='shapeIndex',
# 			closed='closed',
# 			point_count='point_count',
# 		),
# 		dict(
# 			color_r='color_r',
# 			color_g='color_g',
# 			color_b='color_b',
# 			color_a='color_a',
# 			center_x='center_x',
# 			center_y='center_y',
# 			center_z='center_z',
# 			depthLayer='depthLayer',
# 			rotateAxis='rotateAxis',
# 			isTriangle='isTriangle',
# 			pathLength='pathLength',
# 			dupCount='dupCount',
# 		),
# 		(not numericOnly) and dict(
# 			shapeName='shapeName',
# 			path='path',
# 			parentPath='parentPath',
# 		)
# 	)
#
# ShapeAttrMenuSource = common.createMenuSource(
# 	shapeIndex='Shape Index',
# 	#shapeName='Shape Name',
#
# )

def _stringListify(val):
	if isinstance(val, str):
		return val.split(' ')
	if isinstance(val, (list, tuple)):
		return [str(v) for v in val]
	return [str(val)]

class SerializableParams(common.ExtensionBase):
	def __init__(
			self,
			ownerComp,
			includePars: Union[str, Iterable[str]]):
		super().__init__(ownerComp)
		self.includePars = _stringListify(includePars)

	@staticmethod
	def _isExcluded(par):
		return par.isOP or not par.isCustom or par.label.startswith(':')

	def GetParDict(self) -> Dict[str, Any]:
		return {
			par.name: par.eval()
			for par in self.ownerComp.pars(*self.includePars)
			if not self._isExcluded(par)
		}

	def SetParDict(self, vals: Dict[str, Any]):
		vals = vals or {}
		unsupported = set(vals.keys())
		for par in self.ownerComp.pars(*self.includePars):
			if self._isExcluded(par):
				continue
			if par.name not in vals:
				val = None
			else:
				unsupported.remove(par.name)
				val = vals.get(par.name)
			if val is None:
				par.val = par.default
			else:
				par.val = val
		if unsupported:
			self._LogEvent('Unsupported settings ignored: {}'.format(unsupported))

class SerializableComponent(SerializableParams):
	@property
	def _SubStateComps(self) -> List['SerializableParamsOrCOMP']:
		return self.ownerComp.findChildren(maxDepth=1, tags=['subState'])

	def _GetSubCompParDicts(self):
		return {
			comp.name: comp.GetParDict()
			for comp in self._SubStateComps
		}

	def _SetSubCompParDicts(self, vals: Dict[str, Dict[str, Any]]):
		unsupportedComps = set(vals.keys())
		for comp in self._SubStateComps:
			if comp.name not in vals:
				comp.SetParDict({})
			else:
				unsupportedComps.remove(comp.name)
				comp.SetParDict(vals[comp.name])
		if unsupportedComps:
			self._LogEvent('Unsupported sub-components ignored: {}'.format(unsupportedComps))

	def GetComponentSpec(self):
		return PComponentSpec(
			compType=self.par.Comptype.eval(),
			pars=self.GetParDict(),
			subCompPars=self._GetSubCompParDicts())

	def SetComponentSpec(self, spec: PComponentSpec):
		self.SetParDict(spec.pars)
		self._SetSubCompParDicts(spec.subCompPars or {})

SerializableComponentOrCOMP = Union['COMP', SerializableComponent]
SerializableParamsOrCOMP = Union['COMP', SerializableParams]

class ShapeStateGeneratorBase(ShapeStateExt, ABC):
	@abstractmethod
	def SetSpec(self, spec: PShapeStateGenSpec): pass

	@abstractmethod
	def GetSpec(self) -> PShapeStateGenSpec: pass

class RuntimeComponent(common.ExtensionBase, ABC):
	@property
	def _RuntimeApp(self) -> 'RuntimeApp':
		return ext.RuntimeApp

class RuntimeSubsystem(RuntimeComponent):
	@abstractmethod
	def ReadFromProject(self, project: PProject): pass

	@abstractmethod
	def WriteToProject(self, project: PProject): pass
