from common import loggedmethod
from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.source_manager.SourceManagerExt import SourceManager

class SourcesPanel(RuntimeComponent):
	@property
	def _SourceManager(self) -> 'SourceManager':
		return self.par.Sourcemanager.eval()

	@loggedmethod
	def OnCreateMenuItemClick(self, info: dict):
		compType = info['item']
		self._SourceManager.AddSource(PComponentSpec(compType=compType))
