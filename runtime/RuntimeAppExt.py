import common
from common import loggedmethod

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class RuntimeApp(common.ExtensionBase):

	def ShowPatternChooser(self):
		self.op('pattern_chooser_window').par.winopen.pulse()

	def ClosePatternChooser(self):
		self.op('pattern_chooser_window').par.winclose.pulse()

	def ShowUI(self):
		self.op('ui_window').par.winopen.pulse()

	def CloseUI(self):
		self.op('ui_window').par.winclose.pulse()

	@loggedmethod
	def OnChoosePattern(self):
		self.op('pattern_loader').par.Extract.pulse()
		self.ClosePatternChooser()
		self.ShowUI()
		# TODO: other stuff?
