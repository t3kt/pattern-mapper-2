from typing import List, Optional

from common import loggedmethod
from pm2_messaging import Message, MessageHandler
from pm2_project import PProject, PControlBinding, PControlsSettings, ControlTargetCategory
from pm2_runtime_shared import RuntimeSubsystem

# noinspection PyUnreachableCode
if False:
	from _stubs import *
	from runtime.runtime_components.component_manager.ComponentManagerExt import ComponentManager

class ControlManager(RuntimeSubsystem, MessageHandler):
	@loggedmethod
	def Initialize(self):
		self._LoadBindings([])
		self._ComponentManager.ClearComponents()

	def ReadFromProject(self, project: PProject):
		self.par.Enablebindings = False
		settings = project.control or PControlsSettings()
		self._ComponentManager.ReadComponentSpecs(settings.controls or [])
		self._LoadBindings(settings.bindings)
		run('op({!r}).par.Enablebindings = True'.format(self.ownerComp.path), delayFrames=2)

	def WriteToProject(self, project: PProject):
		project.control = PControlsSettings(
			bindings=self._ReadBindings(),
			controls=self._ComponentManager.WriteComponentSpecs()
		)

	@property
	def _ComponentManager(self) -> 'ComponentManager': return self.op('component_manager')

	@property
	def _BindingTable(self) -> 'DAT': return self.op('binding_table')

	@property
	def _ControlTable(self) -> 'DAT': return self.op('control_table')

	@property
	def _CategoryBasePathTable(self) -> 'DAT': return self.op('category_base_paths')

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

	@loggedmethod
	def _AddBinding(self, binding: PControlBinding):
		table = self._BindingTable
		binding.writeRowInTable(table)

	@loggedmethod
	def AddBindingForParam(self, controlName: str, targetPar: 'Par'):
		categoryName = None
		targetOp = targetPar.owner
		for category, path in self._CategoryBasePathTable.rows():
			if targetOp.path.startswith(path.val):
				categoryName = category.val
				break
		if not categoryName:
			self._LogEvent('Unable to find category for {}'.format(targetOp))
			return
		binding = PControlBinding(
			enable=True,
			control=controlName,
			targetCategory=ControlTargetCategory(categoryName),
			targetName=targetOp.name,
			targetParam=targetPar.name,
			rangeLow=targetPar.normMin,
			rangeHigh=targetPar.normMax,
			limitLow=targetPar.min if targetPar.clampMin else targetPar.normMin,
			limitHigh=targetPar.max if targetPar.clampMax else targetPar.normMax,
		)
		self._AddBinding(binding)

	def PrepareBindings(self, dat: 'DAT'):
		dat.clear()
		dat.appendRow(['target', 'targetPath', 'targetParam', 'control', 'rangeLow', 'rangeHigh', 'limitLow', 'limitHigh'])
		bindings = self._ReadBindings()
		controlTable = self._ControlTable
		categoryPathTable = self._CategoryBasePathTable
		categoryContainers = {
			category.val: op(path)
			for category, path in categoryPathTable.rows()
		}
		for binding in bindings:
			if not binding.enable:
				continue
			if not binding.control or not controlTable[binding.control, 0]:
				continue
			if not binding.targetCategory or not binding.targetName or not binding.targetParam:
				continue
			targetParam = None  # type: Optional[Par]
			if binding.targetCategory is not None and binding.targetCategory.name in categoryContainers:
				container = categoryContainers[binding.targetCategory.name]
				targetComp = container.op(binding.targetName)
				if targetComp and hasattr(targetComp.par, binding.targetParam):
					targetParam = getattr(targetComp.par, binding.targetParam)
			if targetParam is None:
				continue
			dat.appendRow([
				'{}:{}'.format(targetParam.owner.path, targetParam.name),
				targetParam.owner.path,
				targetParam.name,
				binding.control,
				binding.rangeLow if binding.rangeLow is not None else 0,
				binding.rangeHigh if binding.rangeHigh is not None else 1,
				binding.limitLow if binding.limitLow is not None else 0,
				binding.limitHigh if binding.limitHigh is not None else 1,
			])

	def HandleMessage(self, message: Message):
		self._ComponentManager.HandleMessage(message)
