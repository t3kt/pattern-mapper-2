from typing import Iterable

import common
from common import formatValue
from pm2_model import PPattern, PShape

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternTableExtractor(common.ExtensionBase):
	def Extract(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		self._BuildShapeTable(self.op('set_shapes'), pattern.shapes)
		self._BuildShapeTable(self.op('set_paths'), pattern.paths)
		pointTable = self.op('set_points')
		self._InitPointsTable(pointTable)
		self._AddPointsToTable(pointTable, pattern.shapes, 'shape')
		self._AddPointsToTable(pointTable, pattern.paths, 'path')

	@staticmethod
	def _BuildShapeTable(dat: 'DAT', shapes: Iterable[PShape]):
		dat.clear()
		dat.appendRow([
			'shapeIndex',
			'shapeName',
			'path',
			'parentPath',
			'closed',
			'points.count',
			'color_r', 'color_g', 'color_b', 'color_a',
			'center_x', 'center_y', 'center_z',
			'depthLayer',
			'rotateAxis',
			'isTriangle',
		])
		for shape in shapes:
			vals = [
				shape.shapeIndex,
				shape.shapeName,
				shape.path,
				shape.parentPath,
				shape.closed,
				len(shape.points),
			]
			vals += list(shape.color) if shape.color else ['', '', '', '']
			vals += list(shape.center) if shape.center else ['', '', '']
			vals += [
				shape.depthLayer,
				shape.rotateAxis,
				shape.isTriangle(),
			]
			dat.appendRow([formatValue(v) for v in vals])

	@staticmethod
	def _InitPointsTable(dat: 'DAT'):
		dat.clear()
		dat.appendRow([
			'shapeType',
			'shapeIndex',
			'pointIndex',
			'pos_x', 'pos_y', 'pos_z',
		])

	@staticmethod
	def _AddPointsToTable(dat: 'DAT', shapes: Iterable[PShape], shapeType: str):
		for shape in shapes:
			for i, point in enumerate(shape.points):
				vals = [
					shapeType,
					shape.shapeIndex,
					i,
				]
				vals += list(point.pos)
				dat.appendRow([formatValue(v) for v in vals])
