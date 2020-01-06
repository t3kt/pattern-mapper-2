from typing import Optional, Union

from common import loggedmethod
from pm2_project import POverrideShapeStateSpec
from pm2_runtime_shared import RuntimeComponent, ShapeStateExt, ShapeStateGeneratorBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class StateGeneratorsPanel(RuntimeComponent):
	@staticmethod
	def OnStateGenMarkerReplicate(comp: 'COMP', target: 'COMP'):
		comp.par.display = True
		comp.par.externaltox = ''
		comp.par.alignorder = comp.digits
		comp.par.Selected.expr = 'parent().par.Selectedgen == {}'.format(comp.digits - 1)
		ctrl = comp.op('amount_slider')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Overrideamount')
		ctrl = comp.op('enable_toggle')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Enableoverride')
		ctrl = comp.op('groups_field')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Groups')
		ctrl = comp.op('invertmask_toggle')
		ctrl.par.Value0.bindExpr = ctrl.shortcutPath(target, toParName='Invertmask')

	def _GetSelectedGen(self) -> Optional[Union['COMP', 'ShapeStateGeneratorBase']]:
		index = int(self.par.Selectedgen)
		genTable = self.op('generators')
		if index < 0 or index >= genTable.numRows:
			return None
		return op(genTable[index + 1, 'path'])

	@loggedmethod
	def BindEditors(self):
		gen = self._GetSelectedGen()
		editor = self.op('state_settings_panel')  # type: Union[COMP, ShapeStateExt]
		self._LogEvent('selected gen: {}'.format(gen))
		# if not gen:
		# 	shapeState = None
		# else:
		# 	spec = gen.GetSpec()  # type: POverrideShapeStateSpec
		# 	shapeState = spec.shapeState
		for editorPar in editor.pars('Include*', 'Fill*', 'Wire*', 'Local*', 'Global*'):
			if gen:
				editorPar.bindExpr = editor.shortcutPath(gen, toParName=editorPar.name)
			else:
				editorPar.bindExpr = ''
				editorPar.val = editorPar.default
