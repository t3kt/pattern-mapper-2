from typing import Union
from common import configurePar

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def prepareComponent(comp: 'Union[str, COMP]'):
	comp = op(comp)
	name = comp.name
	shortcut = parent().par.opshortcut.eval()
	comp.par.clone.expr = "(op.{0}.op({1!r}) if hasattr(op, {0!r}) else None) or ''".format(shortcut, name)
	toxPath = 'shared/{0}/{0}.tox'.format(name)
	toxExpr = "{0!r} if (mod.os.path.exists({0!r}) and me.par.clone.eval() in (None, '', me)) else ''".format(toxPath)
	comp.par.externaltox.expr = toxExpr
	comp.par.reloadcustom.expr = 'me.par.externaltox'
	comp.par.reloadbuiltin.expr = 'me.par.externaltox'

def _setUpTransformParams(page: 'Page', prefix: str):
	configurePar(
		page.appendXYZ(prefix + 't', label=prefix + ' Translate'),
		normMin=-1, normMax=1)
	configurePar(
		page.appendXYZ(prefix + 'r', label=prefix + ' Rotate'),
		normMin=-180, normMax=180)
	configurePar(
		page.appendXYZ(prefix + 's', label=prefix + ' Scale'),
		normMin=-2, normMax=2, default=1)
	configurePar(
		page.appendXYZ(prefix + 'p', label=prefix + ' Pivot'),
		normMin=-1, normMax=1)

def _setUpAppearanceParams(page: 'Page', prefix: str, defaultUVMode: str):
	configurePar(
		page.appendFloat(prefix + 'opacity', label=prefix + ' Opacity'),
		default=1)
	configurePar(
		page.appendRGBA(prefix + 'color', label=prefix + ' Color'),
		default=1)
	_setUpTextureParams(page, prefix + 'tex', defaultUVMode)

def _setUpTextureParams(page: 'Page', prefix: str, defaultUVMode: str):
	configurePar(
		page.appendFloat(prefix + 'opacity', label=prefix + ' Opacity'),
		default=0)
	configurePar(
		page.appendInt(prefix + 'source', label=prefix + ' Source'))
	p = page.appendMenu(prefix + 'uvmode', label=prefix + ' UV Mode')[0]
	p.menuNames = ['loc', 'glob', 'path']
	p.menuLabels = ['Local', 'Global', 'Path']
	p.default = defaultUVMode
	configurePar(
		page.appendXYZ(prefix + 'offset', label=prefix + ' Offset'),
		normMin=-1, normMax=1)
	configurePar(
		page.appendFloat(prefix + 'rotate', label=prefix + ' Rotate'),
		normMin=-180, normMax=180)
	configurePar(
		page.appendFloat(prefix + 'scale', label=prefix + ' Scale'),
		normMin=-2, normMax=2, default=1)

def setUpShapeStateParams(comp: Union[str, COMP]):
	_setUpAppearanceParams(comp.appendCustomPage('Fill'), 'Fill', defaultUVMode='glob')
	_setUpAppearanceParams(comp.appendCustomPage('Wire'), 'Wire', defaultUVMode='path')
	_setUpTransformParams(comp.appendCustomPage('Local'), 'Local')
	_setUpTransformParams(comp.appendCustomPage('Global'), 'Global')
