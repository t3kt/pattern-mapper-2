from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class MainMenu(RuntimeComponent):
	@loggedmethod
	def OnFileAction(self, itemName: str):
		if itemName == 'Open':
			self._RuntimeApp.ShowPatternChooser()
		elif itemName == 'Save':
			self._RuntimeApp.SaveProject()

	@loggedmethod
	def OnEditAction(self, itemName: str):
		pass

	@loggedmethod
	def OnSettingAction(self, itemName: str):
		if itemName == 'Show Preview':
			par = self.ownerComp.parent.ui.par.Showpreview
		elif itemName == 'Show Groups':
			par = self.ownerComp.parent.ui.par.Showgroups
		else:
			return
		par.val = not par.val
