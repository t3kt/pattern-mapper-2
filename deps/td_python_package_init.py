import sys

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def init():
	pkgpath = project.folder + '/deps'

	if pkgpath not in sys.path:
		sys.path.append(pkgpath)

