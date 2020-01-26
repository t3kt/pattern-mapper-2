from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ControlsPanel(RuntimeComponent):
	@staticmethod
	def OnControlReplicate(panel: 'COMP', table: 'DAT'):
		i = panel.digits
		panel.par.clone = op(table[i, 'panel'])
		panel.par.Targetop = op(table[i, 'path'])
		panel.par.display = True
		panel.par.alignorder = i
		panel.par.w.expr = 'me.panelParent().width / 4'
		panel.par.h.expr = 'me.panelParent().height / 4'
