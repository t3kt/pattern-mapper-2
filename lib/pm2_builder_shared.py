from abc import ABC, abstractmethod
from typing import Optional, Iterable, Set, List, Union, Callable
import re

import common
from common import loggedmethod
from pm2_model import PPattern, PShape, PGroup, PSequence
from pm2_settings import PSettings, PGenSpecBase, ShapeSourceAttr, PScope

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


class PatternProcessorBase(common.ExtensionBase, ABC):
	@loggedmethod
	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		settingsJson = self.op('settings_json').text
		settings = PSettings.parseJsonStr(settingsJson)
		pattern = self._ProcessPattern(pattern, settings)
		outputPatternJson = pattern.toJsonStr(minify=self.par.Minifyjson)
		self.op('set_output_pattern_json').text = outputPatternJson

	@abstractmethod
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		pass


class GeneratorBase(common.LoggableSubComponent, ABC):
	def __init__(
			self,
			hostObj,
			genSpec: PGenSpecBase,
			logPrefix: str = None):
		super().__init__(hostObj, logPrefix)
		self.baseName = genSpec.baseName
		if genSpec.suffixes:
			self.suffixes = common.ValueSequence.FromSpec(
				genSpec.suffixes, cyclic=False, backup=lambda i: i)
		else:
			self.suffixes = None

	def _getName(self, index: int, isSolo=False):
		name = self.baseName
		if self.suffixes is None:
			if index == 0 and isSolo and name:
				return name
			suffix = 0
		else:
			suffix = self.suffixes[index]
		return (name or '') + str(suffix)

def _getAlpha(shape: PShape): return shape.color.a if shape.color else 255
def _getValue(shape: PShape):
	return common.colorToHsv(shape.color)[2] if shape.color else 0
def _getZero(_): return 0

_attrGetters = {
	ShapeSourceAttr.alpha: _getAlpha,
	ShapeSourceAttr.value: _getValue,
}

def shapeAttrGetter(attr: ShapeSourceAttr, roundDigits: Optional[int] = None):
	getter = _attrGetters.get(attr)
	if not getter:
		return _getZero
	if not roundDigits:
		return getter
	return lambda shape: round(getter(shape), roundDigits)

class PatternAccessor:
	def __init__(self, pattern: PPattern):
		self.pattern = pattern

	def getGroupsByPatterns(self, groupNamePatterns: Iterable[str]) -> Iterable[PGroup]:
		matchingGroupNames = []
		allGroupNames = [group.groupName for group in self.pattern.groups]
		for pattern in groupNamePatterns:
			for name in mod.tdu.match(pattern, allGroupNames):
				if name not in matchingGroupNames:
					matchingGroupNames.append(name)
		return [
			group
			for group in self.pattern.groups
			if group.groupName in matchingGroupNames
		]

	def getShapeIndicesByGroupPattern(self, groupNamePatterns: Iterable[str]) -> Set[int]:
		shapeIndices = set()
		groups = self.getGroupsByPatterns(groupNamePatterns)
		for group in groups:
			shapeIndices.update(group.shapeIndices)
		return shapeIndices

	def getGroupByName(self, name: str) -> Optional[PGroup]:
		for group in self.pattern.groups:
			if group.groupName == name:
				return group

	def getSequenceByName(self, name: str) -> Optional[PSequence]:
		for sequence in self.pattern.sequences:
			if sequence.sequenceName == name:
				return sequence

	def getGroupOrSequenceByName(self, name: str) -> Optional[Union[PGroup, PSequence]]:
		return self.getGroupByName(name) or self.getSequenceByName(name)

	def getShapesByPathRegex(self, pathPattern: str) -> List[PShape]:
		try:
			return [
				shape
				for shape in self.pattern.shapes
				if re.match(pathPattern, shape.shapePath)
			]
		except TypeError as e:
			print('Invalid path regex: {!r}, {}'.format(pathPattern, e))
			return []

	def getShapesByIndices(self, shapeIndices: Iterable[int]) -> List[PShape]:
		shapeIndices = set(shapeIndices)
		return [
			shape
			for shape in self.pattern.shapes
			if shape.shapeIndex in shapeIndices
		]

	def getPathByPath(self, pathPath: str) -> Optional[PShape]:
		if not self.pattern.paths:
			return None
		for path in self.pattern.paths:
			if path.shapePath == pathPath:
				return path

	def getShapesContainingPoint(self, testPoint: 'tdu.Vector', predicate: Callable[[PShape], bool] = None):
		return [
			shape
			for shape in self.pattern.shapes
			if _shapeContainsPoint(shape, testPoint) and (
					not predicate or predicate(shape))
		]

def createScopes(scopeSpecs: List[PScope]) -> Optional[List[common.ValueSequence]]:
	if not scopeSpecs:
		return None
	return [
		common.ValueSequence.FromSpec(scope.groups, cyclic=False)
		for scope in scopeSpecs
	]

def _shapeContainsPoint(shape: PShape, testPoint: 'tdu.Vector') -> bool:
	testX, testY = testPoint.x, testPoint.y
	shapePoints = [(pt.pos.x, pt.pos.y) for pt in shape.points]
	nShapePoints = len(shapePoints)
	inside = False
	p1x, p1y = shapePoints[0]
	for i in range(nShapePoints + 1):
		p2x, p2y = shapePoints[i % nShapePoints]
		if testY > min(p1y, p2y):
			if testY <= max(p1y, p2y):
				if testX <= max(p1x, p2x):
					if p1y != p2y:
						xints = (testY - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
					else:
						xints = -99999999
					if p1x == p2x or testX <= xints:
						inside = not inside
		p1x, p1y = p2x, p2y
	return inside
