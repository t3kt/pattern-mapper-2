from abc import ABC, abstractmethod
from typing import Optional, Iterable, Set
from colorsys import rgb_to_hsv

import common
from common import loggedmethod
from pm2_model import PPattern, PShape, PGroup
from pm2_settings import PSettings, PGenSpecBase, ShapeSourceAttr

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

def _colorToHsv(color: 'tdu.Color'):
	return rgb_to_hsv(color.r / 255, color.g / 255, color.b / 255)

def _getAlpha(shape: PShape): return shape.color.a if shape.color else 255
def _getValue(shape: PShape):
	return _colorToHsv(shape.color)[2] if shape.color else 0
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
