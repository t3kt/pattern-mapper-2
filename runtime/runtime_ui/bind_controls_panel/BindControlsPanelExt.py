from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.control_manager.ControlManagerExt import ControlManager

class BindControlsPanel(RuntimeComponent):
	def OnMarkerReplicate(self, marker: 'COMP', table: 'DAT', master: 'COMP'):
		i = marker.digits
		marker.par.clone = master
		marker.par.display = True
		marker.par.alignorder = i
		control = op(table[i, 'path'])
		marker.par.Control = control.path
		marker.par.Label = table[i, 'label'] or control.name
		marker.par.drop = 'legacy'
		marker.par.dropscript = self.op('control_marker_dropscript')
		marker.tags.add('ctrlmarker')

	@property
	def _ControlManager(self) -> 'ControlManager': return self.par.Controlmanager.eval()

	@loggedmethod
	def OnMarkerDrop(self, dropName: str, index: int, totalDragged: int, dropExt: str, baseName: str, destPath: str):
		if dropExt == 'parameter':
			targetOp = op(baseName)
			sourceComp = op(destPath)
			if sourceComp.par.parentshortcut == 'marker':
				marker = sourceComp
			else:
				marker = sourceComp.parent.marker
			targetPar = getattr(targetOp.par, dropName)
			self._OnParameterDroppedOnMarker(targetPar, marker)
		else:
			self._LogEvent('Unsupported dropExt: {!r}'.format(dropExt))
			pass

	@loggedmethod
	def _OnParameterDroppedOnMarker(self, targetPar: 'Par', marker: 'COMP'):
		control = marker.par.Control.eval()  # type: COMP
		self._ControlManager.AddBindingForParam(control.name, targetPar)
