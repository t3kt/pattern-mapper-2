from typing import Iterable

import common
from common import formatValue
from pm2_model import PPattern, PShape, PGroup, PSequence
from pm2_model import ModelTableWriter

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternTableExtractor(common.ExtensionBase):
	def Extract(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson or '{}')
		self._BuildInfoTable(self.op('set_info'), pattern)
		self._BuildShapeTable(self.op('set_shapes'), pattern.shapes)
		self._BuildShapeTable(self.op('set_paths'), pattern.paths)
		pointTable = self.op('set_points')
		self._InitPointsTable(pointTable)
		self._AddPointsToTable(pointTable, pattern.shapes, 'shape')
		self._AddPointsToTable(pointTable, pattern.paths, 'path')
		self._BuildGroupTable(self.op('set_groups'), pattern.groups)
		self._BuildSequenceTable(self.op('set_sequences'), pattern.sequences)
		self._BuildSequenceStepTable(self.op('set_sequence_steps'), pattern.sequences)

	@staticmethod
	def _BuildInfoTable(dat: 'DAT', pattern: PPattern):
		dat.clear()
		dat.appendCol([
			'width',
			'height',
			'scale',
			'offset_x',
			'offset_y',
		])
		vals = [
			pattern.width,
			pattern.height,
			pattern.scale if pattern.scale is not None else 1,
			pattern.offset.x if pattern.offset else 0,
			pattern.offset.y if pattern.offset else 0,
		]
		dat.appendCol([formatValue(v) for v in vals])

	@staticmethod
	def _BuildShapeTable(dat: 'DAT', shapes: Iterable[PShape]):
		dat.clear()
		dat.appendRow([
			'shapeIndex',
			'shapeName',
			'path',
			'parentPath',
			'closed',
			'point_count',
			'color_r', 'color_g', 'color_b', 'color_a',
			'color_h', 'color_s', 'color_v',
			'center_x', 'center_y', 'center_z',
			'polarCenter_dist', 'polarCenter_theta', 'polarCenter_phi',
			'depthLayer',
			'rotateAxis',
			'isTriangle',
			'pathLength',
			'dupCount',
		])
		for shape in shapes:
			vals = [
				shape.shapeIndex,
				shape.shapeName,
				shape.shapePath,
				shape.parentPath,
				shape.closed,
				len(shape.points),
			]
			if not shape.color:
				vals += ['', '', '', '', '', '', '']
			else:
				vals += [shape.color.r / 255, shape.color.g / 255, shape.color.b / 255, shape.color.a / 255]
				hsv = common.colorToHsv(shape.color)
				vals += [hsv[0], hsv[1], hsv[2]]
			if not shape.center:
				vals += ['', '', '', '', '', '']
			else:
				vals += list(shape.center)
				vals += common.vectorToSpherical(shape.center)
			vals += [
				shape.depthLayer,
				shape.rotateAxis,
				shape.isTriangle(),
				shape.pathLength,
				shape.dupCount,
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
			'absDist',
			'relDist',
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
				vals += [
					point.absDist, point.relDist,
				]
				dat.appendRow([formatValue(v) for v in vals])

	@staticmethod
	def _BuildGroupTable(dat: 'DAT', groups: Iterable[PGroup]):
		ModelTableWriter(dat).writeGroups(groups)

	@staticmethod
	def BuildShapeGroupMembershipTable(dat: 'DAT', shapeTable: 'DAT', groupTable: 'DAT'):
		ModelTableWriter(dat).writeShapeGroupMemberships(shapeTable, groupTable)

	@staticmethod
	def _BuildSequenceTable(dat: 'DAT', sequences: Iterable[PSequence]):
		ModelTableWriter(dat).writeSequences(sequences)

	@staticmethod
	def _BuildSequenceStepTable(dat: 'DAT', sequences: Iterable[PSequence]):
		ModelTableWriter(dat).writeSequenceSteps(sequences)
