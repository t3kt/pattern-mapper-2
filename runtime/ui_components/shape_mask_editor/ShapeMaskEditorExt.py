from common import ExtensionBase
from pm2_ui import MarkerObject, DropReceiver

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ShapeMaskEditor(ExtensionBase, DropReceiver):
	def HandleCOMPDrop(self, droppedComp: 'COMP', dropTarget: 'COMP') -> bool:
		markerObj = MarkerObject.getFromComp(droppedComp)
		if not markerObj:
			return False
		if markerObj.objectType != 'group':
			self._LogEvent('WARNING: marker type not supported: {}'.format(markerObj))
			return False
		groupName = markerObj.name
		par = self.par.Groups
		par.val = groupName if not par else (par.val + ' ' + groupName)
		return True
