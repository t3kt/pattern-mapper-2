from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_ui.RuntimeUIExt import RuntimeUI

class SequencesPanel(RuntimeComponent):
	def OnPreviewChange(self, highlightedDat: 'DAT'):
		runtimeUI = self._RuntimeApp.UI  # type: RuntimeUI
		if highlightedDat.numRows == 0:
			runtimeUI.Preview.Reset()
		else:
			runtimeUI.Preview.PreviewSequences([c.val for c in highlightedDat.col(0)])
