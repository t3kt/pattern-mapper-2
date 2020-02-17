from typing import Iterable, List

from common import ExtensionBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class RemoteParamBinder(ExtensionBase):
	def OnTextOscReceive(self):
		pass

	def OnTextParamCellChange(self, cells: Iterable['Cell']):
		pathPrefix = '/' + self.par.Pathprefix + '/'
		oscOut = self.op('osctextout')  # type: oscoutDAT
		for cell in cells:
			if cell.col == 0:
				continue
			name = cell.offset(0, -1).val
			val = cell.val
			oscOut.sendOSC(pathPrefix + name, [val])

	def OnTextParamReceive(self, address: str, args: List[str]):
		pathPrefix = '/' + self.par.Pathprefix + '/'
		target = self.par.Targetop.eval()
		if not target:
			return
		name = address[len(pathPrefix):]
		par = getattr(target.par, name, None)
		if par is None:
			return
		par.val = args[0]
