from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class StateGeneratorsPanel(RuntimeComponent):
	@staticmethod
	def OnStateGenMarkerReplicate(comp: 'COMP', target: 'COMP'):
		comp.par.display = True
		comp.par.externaltox = ''
		ctrl = comp.op('amount_slider')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Overrideamount')
		ctrl = comp.op('enable_toggle')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Enableoverride')
		ctrl = comp.op('groups_field')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Groups')
		ctrl = comp.op('invertmask_toggle')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Invertmask')
