from typing import Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def PrepareComponent(comp: 'Union[str, COMP]'):
	comp = op(comp)
	name = comp.name
	shortcut = parent().par.opshortcut.eval()
	comp.par.clone.expr = "(op.{0}.op({1!r}) if hasattr(op, {0!r}) else None) or ''".format(shortcut, name)
	toxPath = 'shared/{0}/{0}.tox'.format(name)
	toxExpr = "{0!r} if (mod.os.path.exists({0!r}) and me.par.clone.eval() in (None, '', me)) else ''".format(toxPath)
	comp.par.externaltox.expr = toxExpr
	comp.par.reloadcustom.expr = 'me.par.externaltox'
	comp.par.reloadbuiltin.expr = 'me.par.externaltox'
