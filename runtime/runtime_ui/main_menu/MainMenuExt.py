from typing import Callable

from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class MainMenu(RuntimeComponent):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.menus = {
			'File': {
				'Open': lambda: self._RuntimeApp.ShowPatternChooser(),
				'Save': lambda: self._RuntimeApp.SaveProject(),
			},
			'View': {
				'Preview': _parToggler(lambda: self._AppSettings.par.Showpreview),
				'Groups': _parToggler(lambda: self._AppSettings.par.Showgroups),
				'Recorder': _windowToggler(lambda: self._RuntimeApp.op('recorder/window')),
				'Output Window': _windowToggler(lambda: self._RuntimeApp.op('output_window')),
			}
		}

	def OnMenuItemClick(self, menuName: str, itemName: str):
		if menuName not in self.menus:
			self._LogEvent('ERROR: menu not supported: {!r} (item: {!r})'.format(menuName, itemName))
			return
		menu = self.menus[menuName]
		if itemName not in menu:
			self._LogEvent('ERROR: menu item not supported: {!r} (item: {!r})'.format(menuName, itemName))
			return
		menu[itemName]()

	@loggedmethod
	def OnFileAction(self, itemName: str):
		self.OnMenuItemClick('File', itemName)

	@loggedmethod
	def OnEditAction(self, itemName: str):
		self.OnMenuItemClick('Edit', itemName)

	@loggedmethod
	def OnViewAction(self, itemName: str):
		self.OnMenuItemClick('View', itemName)

def _parToggler(getPar: Callable[[], 'Par']):
	def action():
		par = getPar()
		par.val = not par.val
	return action

def _windowToggler(getWindow: Callable[[], 'windowCOMP']):
	def action():
		window = getWindow()
		print('toggling window {!r} (open: {})'.format(window, window.isOpen))
		if window.isOpen:
			window.par.winclose.pulse()
		else:
			window.par.winopen.pulse()
	return action
