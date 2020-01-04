from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class MainMenu(RuntimeComponent):
	@loggedmethod
	def OnFileAction(self, itemName: str, info: dict):
		if itemName == 'Open':
			self._RuntimeApp.ShowPatternChooser()
		elif itemName == 'Save':
			self._RuntimeApp.SaveProject()

	@loggedmethod
	def OnEditAction(self, itemName: str, info: dict):
		pass
