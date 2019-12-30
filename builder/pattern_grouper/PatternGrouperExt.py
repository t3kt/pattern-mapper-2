from collections import OrderedDict

import common
from common import simpleloggedmethod
from pm2_model import PPattern, PShape, PGroup
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase
from typing import Dict, Iterable, List, Optional, Set
import re

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternGrouper(PatternProcessorBase):
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		if settings.grouping and settings.grouping.groupGenerators:
			for spec in settings.grouping.groupGenerators:
				self._LogEvent('using group generator {}({})'.format(type(spec), spec))
				generator = _GroupGenerator.fromSpec(self, spec)
				generator.generateGroups(pattern)
		self._LogEvent('Generated {} groups: {}'.format(len(pattern.groups), [group.groupName for group in pattern.groups]))
		return pattern

class _GroupGenerator(common.LoggableSubComponent):
	def __init__(
			self,
			hostObj,
			groupGenSpec: PGroupGenSpec,
			logPrefix: str = None):
		super().__init__(hostObj, logprefix=logPrefix or 'GroupGen')
		self.baseName = groupGenSpec.baseName
		self.suffixes = common.ValueSequence.FromSpec(
			groupGenSpec.suffixes, cyclic=False, backup=lambda i: i) if groupGenSpec.suffixes else None
		attrs = groupGenSpec.attrs or PGroupGenAttrs()
		self.temporary = attrs.temporary
		self.mergeName = attrs.mergeAs
		self.merger = _GroupCombiner(self, boolOp=BoolOp.OR) if self.mergeName else None
		# TODO: rotate axes

	def _getName(self, index: int, isSolo=False):
		name = self.baseName
		if self.suffixes is None:
			if index == 0 and isSolo and name:
				return name
			suffix = 0
		else:
			suffix = self.suffixes[index]
		return (name or '') + str(suffix)

	def _createGroup(
			self,
			groupName: str,
			shapeIndices: List[int] = None,
			skipMerge=False,
	):
		group = PGroup(
			groupName,
			shapeIndices=list(shapeIndices or []),
		)
		if not skipMerge and self.merger is not None:
			self.merger.addGroup(group)
		return group

	def _generateMergedGroup(self, pattern: PPattern):
		if self.merger is None:
			return
		mergedGroup = self._createGroup(
			self.mergeName,
			skipMerge=True,
		)
		if self.merger.buildInto(mergedGroup):
			pattern.groups.append(mergedGroup)

	def generateGroups(self, pattern: PPattern):
		raise NotImplementedError()

	@classmethod
	def fromSpec(cls, hostObj, groupGenSpec: PGroupGenSpec):
		if isinstance(groupGenSpec, PPathGroupGenSpec):
			return _PathGroupGenerator(hostObj, groupGenSpec)
		if isinstance(groupGenSpec, PIdGroupGenSpec):
			return _IdGroupGenerator(hostObj, groupGenSpec)
		raise Exception('Unsupported group gen spec type: {}'.format(type(groupGenSpec)))

class _PathGroupGenerator(_GroupGenerator):
	def __init__(self, hostObj, groupGenSpec: PPathGroupGenSpec, logPrefix='PathGroupGen'):
		super().__init__(hostObj, groupGenSpec, logPrefix=logPrefix)
		self.pathPatterns = common.ValueSequence.FromSpec(groupGenSpec.paths, cyclic=False)
		self.groupAtPathDepth = groupGenSpec.groupAtPathDepth

	@simpleloggedmethod
	def generateGroups(self, pattern: PPattern):
		self._LogEvent('path patterns: {!r}'.format(self.pathPatterns))
		groups = []  # type: List[PGroup]
		n = len(self.pathPatterns)
		for i in range(n):
			pathPattern = self.pathPatterns[i]
			self._LogEvent('trying path pattern: {!r} (type: {})'.format(pathPattern, type(pathPattern)))
			shapes = [
				# shape
				# for shape in pattern.shapes
				# if re.match(pathPattern, shape.shapePath)
			]
			for shape in pattern.shapes:
				if re.match(pathPattern, shape.shapePath):
					self._LogEvent('matched path {!r}'.format(shape.shapePath))
					shapes.append(shape)
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
				group.groupPath = '/'.join(common.longestCommonPrefix([shape.shapePath.split('/') for shape in shapes]))
			groups += groupsForPattern
		if len(groups) == 1 and self.suffixes is None:
			groups[0].groupName = self._getName(0, isSolo=True)
		self._LogEvent('Generated {} groups: {}'.format(len(groups), [group.groupName for group in groups]))
		if not groups:
			return
		pattern.groups += groups
		self._generateMergedGroup(pattern)

	@simpleloggedmethod
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
			pathParts = shape.shapePath.split('/') if shape.shapePath else []
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

def _IdGroupGenerator(hostObj, groupGenSpec: PIdGroupGenSpec):
	return _PathGroupGenerator(
		hostObj,
		PPathGroupGenSpec(
			baseName=groupGenSpec.baseName,
			suffixes=groupGenSpec.suffixes or groupGenSpec.ids,
			attrs=groupGenSpec.attrs,
			paths=[
				'^.*/g\\[id={}\\]'.format(elemId)
				for elemId in groupGenSpec.ids
			] if groupGenSpec.ids else [],
		),
		logPrefix='IdGroupGen',
	)

class _GroupCombiner(common.LoggableSubComponent):
	def __init__(self, hostObj, boolOp: BoolOp):
		super().__init__(hostObj, logprefix='GroupCombiner')
		self.shapeIndices = None  # type: Optional[Set[int]]
		self.groups = []  # type: List[PGroup]
		# self.groupPaths = []  # type: List[str]
		self.boolOp = boolOp or BoolOp

	def addGroup(self, group: PGroup):
		if self.shapeIndices is None:
			self.shapeIndices = set(group.shapeIndices)
		elif self.boolOp == BoolOp.AND:
			self.shapeIndices.intersection_update(group.shapeIndices)
		else:
			self.shapeIndices.update(group.shapeIndices)
		# if group.groupPath:
		# 	self.groupPaths.append(group.groupPath)
		self.groups.append(group)

	def addGroups(self, groups: Iterable[PGroup]):
		for group in groups:
			self.addGroup(group)

	@simpleloggedmethod
	def buildInto(self, resultGroup: PGroup):
		if not self.shapeIndices:
			return False
		resultGroup.shapeIndices = list(sorted(self.shapeIndices))
		# self._LogEvent('group paths: {}'.format(self.groupPaths))
		# if self.groupPaths:
		# 	resultGroup.groupPath = common.longestCommonPrefix(self.groupPaths)
		# 	self._LogEvent('common path: {}'.format(resultGroup.groupPath))
		return True
