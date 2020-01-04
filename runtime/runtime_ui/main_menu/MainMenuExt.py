import common

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.RuntimeAppExt import RuntimeApp

class MainMenu(common.ExtensionBase):
	@property
	def _RuntimeApp(self) -> 'RuntimeApp':
		return ext.RuntimeApp

	def OnFileAction(self, itemName: str, info: dict):
		if itemName == 'Open':
			self._RuntimeApp.ShowPatternChooser()

	def OnEditAction(self, itemName: str, info: dict):
		pass
