from typing import List, Optional

from pm2_project import PProject, PControlBinding, PControlsSettings
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

class ControlManager(RuntimeSubsystem):
	def ReadFromProject(self, project: PProject):
		settings = project.control or PControlsSettings()
		self._ComponentManager.ReadComponentSpecs(settings.controls or [])
		self._LoadBindings(settings.bindings)

	def WriteToProject(self, project: PProject):
		project.control = PControlsSettings(
			bindings=self._ReadBindings(),
			controls=self._ComponentManager.WriteComponentSpecs()
		)

	@property
	def _ComponentManager(self) -> 'ComponentManager':
		return self.op('component_manager')

	@property
	def _BindingTable(self) -> 'DAT':
		return self.op('binding_table')

	def _LoadBindings(self, bindings: List[PControlBinding]):
		table = self._BindingTable
		table.clear()
		table.appendRow(PControlBinding.fieldNames())
		if not bindings:
			return
		for binding in bindings:
			binding.writeRowInTable(table)

	def _ReadBindings(self):
		table = self._BindingTable
		if table.numRows < 2:
			return []
		return [
			PControlBinding.readRowFromTable(table, row)
			for row in range(1, table.numRows)
		]

	def PrepareBindings(self, dat: 'DAT'):
		dat.clear()
		dat.appendRow(['target', 'targetPath', 'targetParam', 'control', 'rangeLow', 'rangeHigh', 'limitLow', 'limitHigh'])
		bindings = self._ReadBindings()
		controlTable = self.op('control_table')  # type: DAT
		categoryPathTable = self.op('category_base_paths')  # type: DAT
		categoryContainers = {
			category.val: op(path)
			for category, path in categoryPathTable.rows()
		}
		for binding in bindings:
			if not binding.enable:
				# dat.appendRow(['DISABLED'])
				continue
			if not binding.control or not controlTable[binding.control, 0]:
				# dat.appendRow(['CONTROL NOT FOUND'])
				continue
			if not binding.targetCategory or not binding.targetName or not binding.targetParam:
				# dat.appendRow(['NO TARGET'])
				continue
			targetParam = None  # type: Optional[Par]
			if binding.targetCategory is not None and binding.targetCategory.name in categoryContainers:
				container = categoryContainers[binding.targetCategory.name]
				targetComp = container.op(binding.targetName)
				if hasattr(targetComp.par, binding.targetParam):
					targetParam = getattr(targetComp.par, binding.targetParam)
			if targetParam is None:
				# dat.appendRow(['TARGET PARAM NOT FOUND'])
				continue
			if binding.limitLow is not None:
				limitLow = binding.limitLow
			elif targetParam.clampMin:
				limitLow = targetParam.min
			else:
				limitLow = -999999
			if binding.limitHigh is not None:
				limitHigh = binding.limitHigh
			elif targetParam.clampMax:
				limitHigh = targetParam.max
			else:
				limitHigh = 999999
			dat.appendRow([
				'{}:{}'.format(targetParam.owner.path, targetParam.name),
				targetParam.owner.path,
				targetParam.name,
				binding.control,
				binding.rangeLow if binding.rangeLow is not None else targetParam.normMin,
				binding.rangeHigh if binding.rangeHigh is not None else targetParam.normMax,
				limitLow,
				limitHigh,
			])
