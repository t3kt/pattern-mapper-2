from typing import Optional, Union

from common import loggedmethod
from pm2_messaging import MessageHandler, Message
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, ShapeStateGeneratorBase
from pm2_ui import UISubSystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.pattern_state_manager.PatternStateManagerExt import PatternStateManager
	from runtime.runtime_components.component_manager_panel.ComponentManagerPanelExt import ComponentManagerPanel

class StateGeneratorsPanel(RuntimeComponent, UISubSystem):
	@property
	def _StateManager(self) -> 'PatternStateManager':
		return self.par.Statemanager.eval()

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

	@property
	def SelectedGenerator(self) -> Optional[Union['COMP', 'ShapeStateGeneratorBase']]:
		index = int(self.par.Selectedgen)
		genTable = self.op('generators')
		if index < 0 or index >= genTable.numRows:
			return None
		return op(genTable[index + 1, 'path'])

	@property
	def PropertiesOP(self):
		subCompsTable = self.op('sub_state_comps')
		compDropMenu = self.op('comp_dropmenu')
		compName = compDropMenu.par.Value0.eval()
		compCell = subCompsTable[compName, 'path']
		# if subCompsTable.numRows < 2:
		if not compCell:
			return self.SelectedGenerator
		return op(compCell) or self.SelectedGenerator

	@loggedmethod
	def OnCreateMenuItemClick(self, info: dict):
		compType = info['item']
		self._StateManager.AddStateGenerator(PComponentSpec(compType=compType))

	def OnStateGenMarkerClick(self, comp: 'COMP'):
		if comp.par.parentshortcut == 'stateGenMarker':
			marker = comp
		else:
			marker = comp.parent.stateGenMarker
		index = marker.digits - 1
		if index == int(self.par.Selectedgen):
			self.par.Selectedgen = -1
		else:
			self.par.Selectedgen = index

	@property
	def _ComponentManagerPanel(self) -> 'ComponentManagerPanel':
		return self.op('component_manager_panel')

	def HandleMessage(self, message: Message):
		self._ComponentManagerPanel.HandleMessage(message)
