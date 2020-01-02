import common
from pm2_state import PShapeState, PAppearance, PTextureAttrs, UVMode, PTransform

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

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

class ShapeStateExt(common.ExtensionBase):
	def LoadShapeState(self, shapeState: PShapeState):
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
			modeName = str(getattr(self.par, prefix + 'uvmode'))
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
		if getattr(self.par, 'Include' + lowPrefix + 'transform'):
			transform.translate = tdu.Vector(self.pars(prefix + 't[xyz]'))
			transform.rotate = tdu.Vector(self.pars(prefix + 'r[xyz]'))
			transform.scale = tdu.Vector(self.pars(prefix + 's[xyz]'))
			transform.pivot = tdu.Vector(self.pars(prefix + 'p[xyz]'))
		if transform.isEmpty():
			return None
		return transform

	def _SetTransform(self, transform: PTransform, prefix: str):
		if not transform:
			transform = PTransform()
		setattr(self.par, 'Include' + prefix.lower() + 'transform', transform.isEmpty())
		if transform.isEmpty():
			for par in self.pars(prefix + '[trsp][xyz]'):
				par.val = par.default
			return
		val = transform.translate or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'tx', val.x)
		setattr(self.par, prefix + 'ty', val.y)
		setattr(self.par, prefix + 'tz', val.z)
		val = transform.rotate or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'rx', val.x)
		setattr(self.par, prefix + 'ry', val.y)
		setattr(self.par, prefix + 'rz', val.z)
		val = transform.scale or tdu.Vector(1, 1, 1)
		setattr(self.par, prefix + 'sx', val.x)
		setattr(self.par, prefix + 'sy', val.y)
		setattr(self.par, prefix + 'sz', val.z)
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
		modePar = getattr(self.par, prefix + 'uvmode')
		modePar.val = texture.uvMode.name if texture.uvMode is not None else modePar.default
		setattr(self.par, 'Include' + lowPrefix + 'textransform', texture.offset is not None or texture.rotate is not None or texture.scale is not None)
		val = texture.offset or tdu.Vector(0, 0, 0)
		setattr(self.par, prefix + 'texoffsetx', val.x)
		setattr(self.par, prefix + 'texoffsety', val.y)
		setattr(self.par, prefix + 'texoffsetz', val.z)
		setattr(self.par, prefix + 'texrotate', texture.rotate or 0)
		setattr(self.par, prefix + 'texscale', texture.scale if texture.scale is not None else 1)
