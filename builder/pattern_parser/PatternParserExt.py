import common
from typing import List
import xml.etree.ElementTree as ET

from pm2_model import PPattern, PPoint, PShape

import td_python_package_init

td_python_package_init.init()

import svg.path as svgpath

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


class PatternParser(common.ExtensionBase):
	def ParsePatternSvg(self):
		pass


class _SvgParser(common.LoggableSubComponent):
	def __init__(self, hostobj):
		super().__init__(hostobj, logprefix='SvgParser')
		self.shapes = []  # type: List[PShape]
		self.paths = []  # type: List[PShape]

	def parse(self, svgXml) -> 'PPattern':
		if not svgXml:
			return PPattern()
		root = ET.fromstring(svgXml)
		width = float(root.get('width', 1))
		height = float(root.get('height', 1))
		self._handleElem(root, 0, nameStack=[])
		return PPattern(
			width=width, height=height,
			shapes=self.shapes,
			paths=self.paths,
		)

	def _handleElem(self, elem: ET.Element, indexInParent: int, nameStack: List[str]):
		elemName = _elemName(elem, indexInParent)
		elemId = elem.get('id', '')
		if elemId.startswith('-') or elem.get('display') == 'none':
			return
		tagName = _localName(elem.tag)
		if tagName == 'path':
			try:
				self._handlePathElem(elem, elemName, nameStack)
			except Exception as e:
				self._LogEvent('Skipping invalid element (nameStack: {}, error: {})'.format(nameStack, e))
		else:
			childNameStack = nameStack + [elemName]
			for childIndex, childElem in enumerate(list(elem)):
				self._handleElem(childElem, childIndex, childNameStack)

	def _handlePathElem(self, pathElem: ET.Element, elemName: str, nameStack: List[str]):
		rawPath = pathElem.get('d')
		path = svgpath.parse_path(rawPath)
		# if len(path) < 2:
		# 	raise Exception('Unsupported path (too short) {}'.format(rawPath))
		firstSegment = path[0]
		if not isinstance(firstSegment, svgpath.Move):
			raise Exception('Unsupported path (must start with Move) {}'.format(rawPath))
		pointPositions = [_pathPoint(firstSegment.start)]
		for segment in path[1:]:
			if isinstance(segment, (svgpath.CubicBezier, svgpath.QuadraticBezier)):
				self._LogEvent('WARNING: treating bezier as line {}...'.format(rawPath[:20]))
			elif not isinstance(segment, svgpath.Line):
				raise Exception('Unsupported path (can only contain Line after first segment) {} {}'.format(
					type(segment), rawPath))
			pathPt = _pathPoint(segment.end)
			pointPositions.append(pathPt)
		# if pointpositions[-1] == pointpositions[0]:
		# 	pointpositions.pop()
		points = [
			PPoint(pos=tuple(pos))
			for pos in pointPositions
		]
		shape = PShape(
			name=pathElem.get('id', None),
			path='/'.join(nameStack + [elemName]),
			parentPath='/'.join(nameStack),
			color=_elemColor(pathElem),
			points=points,
		)
		if path.closed:
			shape.index = len(self.shapes)
			self.shapes.append(shape)
		else:
			shape.index = len(self.paths)
			self.paths.append(shape)

def _elemName(elem: ET.Element, indexInParent: int):
	tagName = _localName(elem.tag)
	elemId = elem.get('id')
	if tagName == 'svg':
		suffix = ''
	elif elemId:
		suffix = '[id={}]'.format(elemId)
	else:
		suffix = '[{}]'.format(indexInParent)
	return tagName + suffix

def _localName(fullName: str):
	if '}' in fullName:
		return fullName.rsplit('}', maxsplit=1)[1]
	elif ':' in fullName:
		return fullName.rsplit(':', maxsplit=1)[1]
	else:
		return fullName

def _pathPoint(pathPt: complex):
	return tdu.Position(pathPt.real, pathPt.imag, 0)

def _elemColor(elem: ET.Element):
	if 'stroke' in elem.attrib:
		return _hexToRgb(elem.attrib['stroke'])
	if 'fill' in elem.attrib:
		return _hexToRgb(elem.attrib['fill'])

def _hexToRgb(hexcolor: str):
	if not hexcolor:
		return None
	if hexcolor.startswith('#'):
		hexcolor = hexcolor[1:]
	return _HEXDEC[hexcolor[0:2]], _HEXDEC[hexcolor[2:4]], _HEXDEC[hexcolor[4:6]]

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
