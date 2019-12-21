import common
from pm2_model import PPattern

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternGeometryBuilder(common.ExtensionBase):
	def BuildPatternGeometry(self, sop):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		sop.clear()
		sop.primAttribs.create('Cd')
		sop.primAttribs.create('shapeIndex', 0)
		sop.primAttribs.create('centerPos', (0.0, 0.0, 0.0))
		sop.primAttribs.create('rotateAxis', (0.0, 0.0, 0.0))
		# distance around path (absolute), distance around path (relative to shape length)
		sop.vertexAttribs.create('absRelDist', (0.0, 0.0))
		self._AddShapes(sop, pattern)

	@staticmethod
	def _AddShapes(sop, pattern: PPattern):
		for shape in pattern.shapes:
			poly = sop.appendPoly(
				len(shape.points),
				addPoints=True,
				closed=shape.closed is not False,
			)
			poly.shapeIndex[0] = shape.shapeIndex
			poly.rotateAxis = 0, 0, shape.rotateAxis or 0
			poly.centerPos = tuple(shape.centerOrAverage())
			if shape.color:
				poly.Cd = tuple(shape.color / 255.0)
			else:
				poly.Cd = 1, 1, 1, 1

			for i, point in enumerate(shape.points):
				vertex = poly[i]
				vertex.point.P = point.pos
				vertex.absRelDist[0] = point.absDist or 0.0
				vertex.absRelDist[1] = point.relDist or 0.0
