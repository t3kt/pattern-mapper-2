from collections import OrderedDict

import common
from common import loggedmethod, simpleloggedmethod
from pm2_model import PPattern, PShape, PGroup
from pm2_settings import PSettings, PGroupGenSpec, PPathGroupGenSpec
from typing import Dict, List
import re

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternGrouper(common.ExtensionBase):
	@loggedmethod
	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		settingsJson = self.op('settings_json').text
		settings = PSettings.parseJsonStr(settingsJson)
		self._LogEvent('settings: {}'.format(settings))
		if settings.grouping:
			for spec in settings.grouping.groupGenerators:
				self._LogEvent('using group generator {}({})'.format(type(spec), spec))
				generator = _GroupGenerator.fromSpec(self, spec)
				generator.generateGroups(pattern)
		outputPatternJson = pattern.toJsonStr(minify=self.par.Minifyjson)
		self.op('set_output_pattern_json').text = outputPatternJson

class _GroupGenerator(common.LoggableSubComponent):
	def __init__(
			self,
			hostObj,
			groupGenSpec: PGroupGenSpec,
			logPrefix: str = None):
		super().__init__(hostObj, logprefix=logPrefix or 'GroupGen')
		self.baseName = groupGenSpec.groupName
		self.suffixes = common.ValueSequence.FromSpec(
			groupGenSpec.suffixes, cyclic=False, backup=lambda i: i) if groupGenSpec.suffixes else None
		self.temporary = groupGenSpec.temporary
		# TODO: merging
		# TODO: rotate axes

	def _getName(self, index: int, isSolo=False):
		name = self.baseName
		if self.suffixes is None:
			if index == 0 and isSolo and name:
				return name
			suffix = 0
		else:
			suffix = self.suffixes[index]
		return (self.baseName or '') + str(suffix)

	@staticmethod
	def _createGroup(
			groupName: str,
			shapeIndices: List[int] = None,
	):
		group = PGroup(
			groupName,
			shapeIndices=list(shapeIndices),
		)
		return group

	def generateGroups(self, pattern: PPattern):
		raise NotImplementedError()

	@classmethod
	def fromSpec(cls, hostObj, groupGenSpec: PGroupGenSpec):
		if isinstance(groupGenSpec, PPathGroupGenSpec):
			return _PathGroupGenerator(hostObj, groupGenSpec)
		raise Exception('Unsupported group gen spec type: {}'.format(type(groupGenSpec)))

class _PathGroupGenerator(_GroupGenerator):
	def __init__(self, hostObj, groupGenSpec: PPathGroupGenSpec):
		super().__init__(hostObj, groupGenSpec, logPrefix='PathGroupGen')
		self.pathPatterns = common.ValueSequence.FromSpec(groupGenSpec.paths, cyclic=False)
		self.groupAtPathDepth = groupGenSpec.groupAtPathDepth

	@simpleloggedmethod
	def generateGroups(self, pattern: PPattern):
		groups = []  # type: List[PGroup]
		n = len(self.pathPatterns)
		for i in range(n):
			pathPattern = self.pathPatterns[i]
			shapes = [
				shape
				for shape in pattern.shapes
				if re.match(pathPattern, shape.path)
			]
			if not shapes:
				continue
			if self.groupAtPathDepth is None:
				groupsForPattern = [
					self._createGroup(
						self._getName(i, isSolo=n == 1),
						shapeIndices=[shape.shapeIndex for shape in shapes],
					)
				]
			else:
				groupsForPattern = self._groupsFromPathMatches(
					self._getName(i, isSolo=n == 1),
					shapes=shapes,
				)
			for group in groupsForPattern:
				group.groupPath = '/'.join(common.longestCommonPrefix([shape.path.split('/') for shape in shapes]))
			groups += groupsForPattern
		if len(groups) == 1 and self.suffixes is None:
			groups[0].groupName = self._getName(0, isSolo=True)
		pattern.groups += groups

	@loggedmethod
	def _groupsFromPathMatches(self, baseName: str, shapes: List[PShape]) -> List[PGroup]:
		if self.groupAtPathDepth == 0:
			return [
				self._createGroup(
					'{}_{}'.format(baseName, i),
					shapeIndices=[shape.shapeIndex],
				)
				for i, shape in enumerate(shapes)
			]
		shapesByPrefix = OrderedDict()  # type: Dict[str, List[PShape]]
		for shape in shapes:
			pathParts = shape.path.split('/') if shape.path else []
			prefix = '/'.join(pathParts[:self.groupAtPathDepth])
			if prefix not in shapesByPrefix:
				shapesByPrefix[prefix] = []
			shapesByPrefix[prefix].append(shape)
		return [
			self._createGroup(
				'{}_{}'.format(baseName, i),
				shapeIndices=[shape.shapeIndex for shape in groupShapes],
			)
			for i, groupShapes in enumerate(shapesByPrefix.values())
		]
