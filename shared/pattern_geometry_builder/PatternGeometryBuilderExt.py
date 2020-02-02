import common
from pm2_model import PPattern, PShape

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

remap = tdu.remap

class PatternGeometryBuilder(common.ExtensionBase):
	def BuildPatternGeometry(self, sop: 'scriptSOP'):
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

	def _AddShapes(self, sop, pattern: PPattern):
		for shape in pattern.shapes:
			self._AddShape(sop, shape)

	@staticmethod
	def _AddShape(sop: 'scriptSOP', shape: PShape):
		poly = sop.appendPoly(
			len(shape.points),
			addPoints=True,
			closed=shape.closed is not False,
		)
		poly.shapeIndex[0] = shape.shapeIndex
		poly.rotateAxis = 0, 0, shape.rotateAxis or 0
		poly.centerPos = tuple(shape.centerOrAverage())
		color = shape.color or (255, 255, 255, 255)
		poly.Cd[0] = color[0] / 255
		poly.Cd[1] = color[1] / 255
		poly.Cd[2] = color[2] / 255
		poly.Cd[3] = color[3] / 255

		for i, point in enumerate(shape.points):
			vertex = poly[i]
			vertex.point.P = point.pos
			vertex.absRelDist[0] = point.absDist or 0.0
			vertex.absRelDist[1] = point.relDist or 0.0

	@staticmethod
	def SetUVLayerToLocalPos(sop, uvlayer: int):
		for prim in sop.prims:
			for vertex in prim:
				vertex.uv[(uvlayer * 3) + 0] = remap(vertex.point.x, prim.min.x, prim.max.x, 0, 1)
				vertex.uv[(uvlayer * 3) + 1] = remap(vertex.point.y, prim.min.y, prim.max.y, 0, 1)

	def FixFaceFlipping(self, sop: 'scriptSOP'):
		for poly in sop.prims:
			self._FixFaceFlipping(poly)

	@staticmethod
	def _FixFaceFlipping(poly: Poly):
		if poly.normal.z >= 0:
			return
		origPoints = [v.point for v in poly]
		origUVs = [_attrDataToTuple(v.uv) for v in poly]
		for i in range(len(poly)):
			poly[i].point = origPoints[-i]
			_setAttrDataFromTuple(poly[i].uv, origUVs[-i])

def _attrDataToTuple(attrData: 'AttributeData'):
	return tuple(attrData[i] for i in range(len(attrData)))

def _setAttrDataFromTuple(attrData: 'AttributeData', values: tuple):
	for i in range(len(values)):
		attrData[i] = values[i]

# def fixFaceFlipping(sop):
# 	for prim in sop.prims:
# 		if prim.normal.z < 0:
# 			origpoints = [v.point for v in prim]
# 			origuvs = [_attrDataToTuple(v.uv) for v in prim]
# 			n = len(prim)
# 			for i in range(n):
# 				prim[i].point = origpoints[-i]
# 				_setAttrDataFromTuple(prim[i].uv, origuvs[-i])
