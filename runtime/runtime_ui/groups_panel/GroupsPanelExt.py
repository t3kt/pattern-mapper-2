from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_ui.RuntimeUIExt import RuntimeUI

class GroupsPanel(RuntimeComponent):
	def OnPreviewChange(self, highlightedGroupsDat: 'DAT'):
		runtimeUI = self._RuntimeApp.UI  # type: RuntimeUI
		if highlightedGroupsDat.numRows == 0:
			runtimeUI.Preview.Reset()
		else:
			runtimeUI.Preview.PreviewGroups([c.val for c in highlightedGroupsDat.col(0)])
