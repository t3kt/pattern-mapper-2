import sys

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


def init():
	proj = globals().get('project')
	if not proj:
		return
	pkgpath = proj.folder + '/deps'

	if pkgpath not in sys.path:
		sys.path.append(pkgpath)

