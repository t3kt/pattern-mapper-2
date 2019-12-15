import common
import json

from pm2_model import PPattern, PShape
from pm2_settings import PPreProcSettings, PSettings, BoundType

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternPreProcessor(common.ExtensionBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)

	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		inputPatternObj = json.loads(inputPatternJson or '{}')
		pattern = PPattern.fromJsonDict(inputPatternObj)
		settingsJson = self.op('settings_json').text
		settingsObj = json.loads(settingsJson or '{}')
		settings = PSettings.fromJsonDict(settingsObj)
		processor = _PreProcessor(self, settings.preProc)
		processor.process(pattern)
		outputPatternJson = json.dumps(pattern.toJsonDict(), indent=None if self.par.Minifyjson else '  ')
		self.op('set_output_pattern_json').text = outputPatternJson

class _PreProcessor(common.LoggableSubComponent):
	def __init__(self, hostObj, settings: PPreProcSettings):
		super().__init__(hostObj, logprefix='PreProc')
		self.settings = settings or PPreProcSettings()
		self.pattern = PPattern()
		self.minBound = tdu.Vector(0, 0, 0)
		self.maxBound = tdu.Vector(0, 0, 0)
		self.scale = 1

	def process(self, pattern: PPattern):
		self.pattern = pattern or PPattern()
		if not self.pattern.shapes and not self.pattern.paths:
			return
		shapePointPositions = [
			v
			for shape in self.pattern.shapes
			for v in shape.pointPositions()
		]
		self.minBound = common.aggregateTduVectors(shapePointPositions, min)
		self.maxBound = common.aggregateTduVectors(shapePointPositions, max)
		if self.settings.recenter:
			self._recenterCoords()
		if self.settings.rescale:
			self._rescaleCoords()

	def _recenterCoords(self):
		if self.settings.recenter.centerOnShape:
			shapeNames = self.settings.recenter.centerOnShape.split(' ')
			centers = []
			for shapeName in shapeNames:
				shape = self._getShapeByName(shapeName)
				if shape:
					centers.append(shape.centerOrAverage())
			if not centers:
				self._LogEvent('Unable to find shape for recentering: {!r}'.format(self.settings.recenter.centerOnShape))
				return
			center = common.averageTduVectors(centers)
		elif self.settings.recenter.boundType == BoundType.shapes:
			center = common.averageTduVectors([self.minBound, self.maxBound])
		else:
			center = tdu.Vector(self.pattern.width / 2, self.pattern.height / 2, 0)
		offset = -center
		if offset == tdu.Vector(0, 0, 0):
			return
		for shape in self.pattern.shapes:
			_offsetShapePoints(shape, offset)
		for path in self.pattern.paths:
			_offsetShapePoints(path, offset)
		self.minBound += offset
		self.maxBound += offset
		self.pattern.offset = (self.pattern.offset or tdu.Vector(0, 0, 0)) + offset

	def _rescaleCoords(self):
		if self.settings.rescale.bound == BoundType.shapes:
			size = self.maxBound - self.minBound
		else:
			size = tdu.Vector(self.pattern.width, self.pattern.height, 0)
		self.scale = 1 / max(size.x, size.y, size.z)
		for shape in self.pattern.shapes:
			_scaleShapePoints(shape, self.scale)
		for path in self.pattern.paths:
			_scaleShapePoints(path, self.scale)
		if self.pattern.scale is None:
			self.pattern.scale = 1
		self.pattern.scale *= self.scale

	def _getShapeByName(self, shapeName):
		if not shapeName or not self.pattern.shapes:
			return None
		for shape in self.pattern.shapes:
			if shape.shapeName == shapeName:
				return shape

def _offsetShapePoints(shape: PShape, offset: tdu.Vector):
	for point in shape.points:
		point.pos += offset
	if shape.center:
		shape.center += offset

def _scaleShapePoints(shape: PShape, scale: float):
	for point in shape.points:
		point.pos *= scale
	if shape.center:
		shape.center *= scale
