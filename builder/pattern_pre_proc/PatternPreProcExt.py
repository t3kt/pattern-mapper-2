import common
import json

from pm2_model import PPattern, PPoint, PShape
from pm2_settings import PPreProcSettings, PSettings

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
			for v in shape.pointPosVectors()
		]
		self.minBound = common.aggregateTduVectors(shapePointPositions, min)
		self.maxBound = common.aggregateTduVectors(shapePointPositions, max)
		if self.settings.recenter:
			self._recenterCoords()
		if self.settings.rescale:
			self._rescaleCoords()
		pass

	def _recenterCoords(self):
		if self.settings.recenter.centerOnShape:
			shapeNames = self.settings.recenter.centerOnShape.split(' ')
			centerShapes = []
			for shapeName in shapeNames:
				shape = self._getShapeByName(shapeName)
				if shape:
					centerShapes.append(shape)
			if not centerShapes:
				self._LogEvent('Unable to find shape for recentering: {!r}'.format(self.settings.recenter.centerOnShape))
				return
		else:
			pass
		raise NotImplementedError()

	def _rescaleCoords(self):
		pass

	def _getShapeByName(self, shapeName):
		if not shapeName or not self.pattern.shapes:
			return None
		for shape in self.pattern.shapes:
			if shape.shapeName == shapeName:
				return shape

def _average(vals):
	vals = list(vals)
	return sum(vals) / len(vals)
