from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class BindControlsPanel(RuntimeComponent):
	@staticmethod
	def OnMarkerReplicate(marker: 'COMP', table: 'DAT', master: 'COMP'):
		i = marker.digits
		marker.par.clone = master
		marker.par.display = True
		marker.par.alignorder = i
		control = op(table[i, 'path'])
		marker.par.Control = control.path
		marker.par.Label = table[i, 'label'] or control.name
