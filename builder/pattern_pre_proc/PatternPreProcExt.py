import math

import common
from common import loggedmethod, simpleloggedmethod
from pm2_model import PPattern, PShape
from pm2_settings import PPreProcSettings, PSettings, BoundType
from typing import List

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternPreProcessor(common.ExtensionBase):
	@loggedmethod
	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		settingsJson = self.op('settings_json').text
		settings = PSettings.parseJsonStr(settingsJson)
		processor = _PreProcessor(self, settings.preProc)
		processor.process(pattern)
		outputPatternJson = pattern.toJsonStr(minify=self.par.Minifyjson)
		self.op('set_output_pattern_json').text = outputPatternJson

class _PreProcessor(common.LoggableSubComponent):
	def __init__(self, hostObj, settings: PPreProcSettings):
		super().__init__(hostObj, logprefix='PreProc')
		self.settings = settings or PPreProcSettings()
		self.pattern = PPattern()
		self.minBound = tdu.Vector(0, 0, 0)
		self.maxBound = tdu.Vector(0, 0, 0)
		self.scale = 1

	@simpleloggedmethod
	def process(self, pattern: PPattern):
		self._LogEvent('Processing')
		self.pattern = pattern or PPattern()
		if not self.pattern.shapes and not self.pattern.paths:
			self._LogEvent('No shapes or paths')
			return
		self._LogEvent('proc settings: {}'.format(self.settings))
		shapePointPositions = [
			v
			for shape in self.pattern.shapes
			for v in shape.pointPositions()
		]
		self.minBound = common.aggregateTduVectors(shapePointPositions, min)
		self.maxBound = common.aggregateTduVectors(shapePointPositions, max)
		self._calculateCenters()
		if self.settings.recenter:
			self._recenterCoords()
		if self.settings.rescale:
			self._rescaleCoords()

	@loggedmethod
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
		elif self.settings.recenter.bound == BoundType.shapes:
			center = common.averageTduVectors([self.minBound, self.maxBound])
		else:
			center = tdu.Vector(self.pattern.width / 2, self.pattern.height / 2, 0)
		offset = -center
		if offset == tdu.Vector(0, 0, 0):
			return
		self._LogEvent('Offset: {}'.format(offset))
		for shape in self.pattern.shapes:
			_offsetShapePoints(shape, offset)
		for path in self.pattern.paths:
			_offsetShapePoints(path, offset)
		self.minBound += offset
		self.maxBound += offset
		self.pattern.offset = (self.pattern.offset or tdu.Vector(0, 0, 0)) + offset

	@loggedmethod
	def _rescaleCoords(self):
		if self.settings.rescale.bound == BoundType.shapes:
			size = self.maxBound - self.minBound
		else:
			size = tdu.Vector(self.pattern.width, self.pattern.height, 0)
		self.scale = 1 / max(size.x, size.y, size.z)
		self._LogEvent('Scale: {}'.format(self.scale))
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

	def _calculateCenters(self):
		self._LogEvent('Calculating shape centers (fix triangles: {})'.format(self.settings.fixTriangleCenters))
		for shape in self.pattern.shapes:
			self._calculateShapeCenter(shape)
		for path in self.pattern.paths:
			self._calculateShapeCenter(path)

	def _calculateShapeCenter(self, shape: PShape):
		if shape.isTriangle() and self.settings.fixTriangleCenters:
			self._fixTriangleCenter(shape)
		else:
			shape.center = shape.centerOrAverage()

	def _fixTriangleCenter(self, shape: PShape):
		positions = shape.pointPositions()
		try:
			shape.center = _getTriangleCenter(positions)
			return
		except Exception as e:
			self._LogEvent(e)
		shape.center = shape.centerOrAverage()

	def _calculatePointDistances(self):
		for shape in self.pattern.shapes:
			self._calculateShapePointDistances(shape)
		for path in self.pattern.paths:
			self._calculateShapePointDistances(path)

	def _calculateShapePointDistances(self, shape: PShape):
		totalDist = 0
		prevPoint = shape.points[0]
		prevPoint.absDist = 0
		prevPoint.relDist = 0
		for point in shape.points[1:]:
			segDist = prevPoint.pos.distance(point.pos) * self.scale
			totalDist += segDist
			point.absDist = totalDist
		if shape.closed and len(shape.points) > 2:
			totalDist += shape.points[-1].pos.distance(shape.points[0].pos) * self.scale
		for point in shape.points:
			point.absDist = point.relDist / totalDist
		shape.pathLength = totalDist

def _getTriangleCenter(positions: List[tdu.Vector]):
	if len(positions) != 3:
		raise Exception('Shape is not a triangle (wrong number of points: {})'.format(positions))
	pt1, pt2, pt3 = positions
	if pt1[2] != pt2[2] or pt1[2] != pt3[2]:
		raise Exception('Points must have the same depth')
	opposite1 = common.averageTduVectors([pt2, pt3])
	opposite2 = common.averageTduVectors([pt1, pt3])
	centerx, centery, valid, r, s = _intersectLines(
		(pt1[0], pt1[1]), (opposite1[0], opposite1[1]),
		(pt2[0], pt2[1]), (opposite2[0], opposite2[1]))
	if not valid:
		raise Exception('Invalid triangle')
	return tdu.Vector(centerx, centery, pt1[2])


# https://www.cs.hmc.edu/ACM/lectures/intersections.html
def _intersectLines(pt1, pt2, ptA, ptB):
	""" this returns the intersection of Line(pt1,pt2) and Line(ptA,ptB)

			returns a tuple: (xi, yi, valid, r, s), where
			(xi, yi) is the intersection
			r is the scalar multiple such that (xi,yi) = pt1 + r*(pt2-pt1)
			s is the scalar multiple such that (xi,yi) = pt1 + s*(ptB-ptA)
					valid == 0 if there are 0 or inf. intersections (invalid)
					valid == 1 if it has a unique intersection ON the segment    """

	DET_TOLERANCE = 0.00000001

	# the first line is pt1 + r*(pt2-pt1)
	# in component form:
	x1, y1 = pt1
	x2, y2 = pt2
	dx1 = x2 - x1
	dy1 = y2 - y1

	# the second line is ptA + s*(ptB-ptA)
	x, y = ptA
	xB, yB = ptB
	dx = xB - x
	dy = yB - y

	# we need to find the (typically unique) values of r and s
	# that will satisfy
	#
	# (x1, y1) + r(dx1, dy1) = (x, y) + s(dx, dy)
	#
	# which is the same as
	#
	#    [ dx1  -dx ][ r ] = [ x-x1 ]
	#    [ dy1  -dy ][ s ] = [ y-y1 ]
	#
	# whose solution is
	#
	#    [ r ] = _1_  [  -dy   dx ] [ x-x1 ]
	#    [ s ] = DET  [ -dy1  dx1 ] [ y-y1 ]
	#
	# where DET = (-dx1 * dy + dy1 * dx)
	#
	# if DET is too small, they're parallel
	#
	DET = (-dx1 * dy + dy1 * dx)

	if math.fabs(DET) < DET_TOLERANCE:
		return 0, 0, 0, 0, 0

	# now, the determinant should be OK
	DETinv = 1.0 / DET

	# find the scalar amount along the "self" segment
	r = DETinv * (-dy * (x - x1) + dx * (y - y1))

	# find the scalar amount along the input line
	s = DETinv * (-dy1 * (x - x1) + dx1 * (y - y1))

	# return the average of the two descriptions
	xi = (x1 + r * dx1 + x + s * dx) / 2.0
	yi = (y1 + r * dy1 + y + s * dy) / 2.0
	return xi, yi, 1, r, s

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
