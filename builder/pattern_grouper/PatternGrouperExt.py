from collections import OrderedDict

import common
from common import simpleloggedmethod
from pm2_model import PPattern, PShape, PGroup
from pm2_settings import *
from pm2_builder_shared import PatternProcessorBase, GeneratorBase, PatternAccessor
from typing import Dict, Iterable, List, Optional, Set

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
				prevGroups = generator.generateGroups(pattern)
				if prevGroups and spec.attrs and spec.attrs.mergeAs:
					mergeSpec = PMergeGroupGenSpec(
						baseName=spec.attrs.mergeAs,
						boolOp=BoolOp.OR,
						groups=[group.groupName for group in prevGroups],
					)
					self._LogEvent(f'using merge group generator {mergeSpec}')
					generator = _MergeGroupGenerator(self, mergeSpec)
					generator.generateGroups(pattern)
		self._LogEvent('Generated {} groups: {}'.format(len(pattern.groups), [group.groupName for group in pattern.groups]))
		return pattern

class _GroupGenerator(GeneratorBase):
	def __init__(
			self,
			hostObj,
			groupGenSpec: PGroupGenSpec,
			logPrefix: str = None):
		super().__init__(
			hostObj,
			groupGenSpec,
			logPrefix=logPrefix or 'GroupGen')
		attrs = groupGenSpec.attrs or PGroupGenAttrs()
		self.temporary = attrs.temporary
		# TODO: rotate axes

	def _createGroup(
			self,
			groupName: str,
			shapeIndices: List[int] = None,
	):
		group = PGroup(
			groupName,
			shapeIndices=list(shapeIndices or []),
			temporary=self.temporary,
		)
		return group

	def generateGroups(self, pattern: PPattern) -> List[PGroup]:
		raise NotImplementedError()

	@classmethod
	def fromSpec(cls, hostObj, groupGenSpec: PGroupGenSpec):
		if isinstance(groupGenSpec, PXmlPathGroupGenSpec):
			return _XmlPathGroupGenerator(hostObj, groupGenSpec)
		if isinstance(groupGenSpec, PIdGroupGenSpec):
			return _IdGroupGenerator(hostObj, groupGenSpec)
		if isinstance(groupGenSpec, PMergeGroupGenSpec):
			return _MergeGroupGenerator(hostObj, groupGenSpec)
		raise Exception('Unsupported group gen spec type: {}'.format(type(groupGenSpec)))

class _XmlPathGroupGenerator(_GroupGenerator):
	def __init__(self, hostObj, groupGenSpec: PXmlPathGroupGenSpec, logPrefix='XmlPathGroupGen'):
		super().__init__(hostObj, groupGenSpec, logPrefix=logPrefix)
		self.pathPatterns = common.ValueSequence.FromSpec(groupGenSpec.paths, cyclic=False)
		self.groupAtPathDepth = groupGenSpec.groupAtPathDepth

	@simpleloggedmethod
	def generateGroups(self, pattern: PPattern) -> List[PGroup]:
		self._LogEvent('path patterns: {!r}'.format(self.pathPatterns))
		groups = []  # type: List[PGroup]
		n = len(self.pathPatterns)
		patternAccessor = PatternAccessor(pattern)
		for i in range(n):
			pathPattern = self.pathPatterns[i]
			self._LogEvent('trying path pattern: {!r} (type: {})'.format(pathPattern, type(pathPattern)))
			shapes = patternAccessor.getShapesByPathRegex(pathPattern)
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
			return []
		pattern.groups += groups
		return groups

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
	return _XmlPathGroupGenerator(
		hostObj,
		PXmlPathGroupGenSpec(
			baseName=groupGenSpec.baseName,
			suffixes=groupGenSpec.suffixes or groupGenSpec.ids,
			attrs=groupGenSpec.attrs,
			paths=[
				'^.*/(g|path)\\[id={}\\]'.format(elemId)
				for elemId in groupGenSpec.ids
			] if groupGenSpec.ids else [],
		),
		logPrefix='IdGroupGen',
	)

class _MergeGroupGenerator(_GroupGenerator):
	def __init__(self, hostObj, groupGenSpec: PMergeGroupGenSpec, logPrefix='MergeGroupGen'):
		super().__init__(hostObj, groupGenSpec, logPrefix=logPrefix)
		self.groupNames = common.ValueSequence.FromSpec(groupGenSpec.groups, cyclic=False)
		self.merger = _GroupCombiner(self, boolOp=groupGenSpec.boolOp or BoolOp.OR)

	@simpleloggedmethod
	def generateGroups(self, pattern: PPattern) -> List[PGroup]:
		patternAccessor = PatternAccessor(pattern)
		groups = patternAccessor.getGroupsByPatterns(self.groupNames)
		if not groups:
			self._LogEvent(f'No groups found matching patterns: {self.groupNames.vals}')
			return []
		self.merger.addGroups(groups)
		mergedGroup = self._createGroup(
			self._getName(0, isSolo=True),
		)
		self.merger.buildInto(mergedGroup)
		pattern.groups.append(mergedGroup)
		return [mergedGroup]

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
