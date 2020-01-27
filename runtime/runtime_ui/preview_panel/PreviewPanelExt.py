from typing import List

from common import loggedmethod
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PreviewPanel(RuntimeComponent):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.state = self.op('state')

	@loggedmethod
	def Initialize(self):
		self.Reset()

	@loggedmethod
	def PreviewGroups(self, groupNames: List[str]):
		if not groupNames:
			self.Reset()
			return
		self.state.par.Previewmode = 'group'
		self.state.par.Highlightgroups = ' '.join(map(str, groupNames))

	@loggedmethod
	def Reset(self):
		self.state.par.Previewmode = 'default'
		self.state.par.Highlightgroups = ''
