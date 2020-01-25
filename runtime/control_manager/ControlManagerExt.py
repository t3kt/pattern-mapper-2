from typing import List

from pm2_project import PProject, PControlBinding
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ControlManager(RuntimeSubsystem):
	def ReadFromProject(self, project: PProject):
		pass

	def WriteToProject(self, project: PProject):
		pass

	@property
	def _BindingTable(self) -> 'DAT':
		return self.op('binding_table')

	def _LoadBindings(self, bindings: List[PControlBinding]):
		table = self._BindingTable
		table.clear()
		table.appendRow(PControlBinding.fieldNames())
		raise NotImplementedError()
