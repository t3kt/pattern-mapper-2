from dataclasses import dataclass
from typing import Optional, List, Any

from common import ExtensionBase, createOP, OPAttrs, formatValue
from pm2_messaging import Message, MessageHandler, CommonMessages

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.RuntimeAppExt import RuntimeApp

class ParameterBindHost(ExtensionBase, MessageHandler):
	def Reset(self):
		table = self._GetTable(autoInit=False)
		if not table or table.numRows < 2:
			return
		table.setSize(1, table.numCols)
		self.RebuildParameters()

	def RegisterComponent(self, comp: 'COMP', channelPath: str):
		table = self._GetTable(autoInit=True)
		table.appendRow([comp.path, channelPath])
		self.RebuildParameters()

	def _GetTable(self, autoInit=False) -> Optional['DAT']:
		table = self.par.Comptable.eval()
		if not table and autoInit:
			return self._AutoInitTable()
		return table

	def _AutoInitTable(self):
		par = self.par.Comptable
		table = par.eval()  # type: DAT
		if table is None:
			tableName = par.val or 'param_bind_table'
			table = self.ownerComp.parent().create(tableDAT, tableName)
			table.nodeX = self.ownerComp.nodeX
			table.nodeY = self.ownerComp.nodeY - self.ownerComp.nodeHeight - 50
			par.val = table.name
		if table.numRows == 0 or (table.numRows == 1 and table.numCols == 1 and table[0, 0] == ''):
			table.clear()
			table.appendRow(['component', 'channelPath'])
		elif table[0, 0] != 'component' or table[0, 1] != 'channelPath':
			if table.numCols < 2:
				table.setSize(table.numRows, 2)
			table[0, 0] = 'component'
			table[0, 1] = 'channelPath'
		return table

	def CreateTable(self):
		self._AutoInitTable()

	def PrepareCompTable(self, dat: 'DAT', compTable: 'DAT'):
		dat.clear()
		dat.appendRow(compTable.row(0))
		dat.appendCol(['numericParams'])
		dat.appendCol(['textParams'])
		for inputRow in range(1, compTable.numRows):
			comp = self.ownerComp.op(compTable[inputRow, 'component'])
			if not comp:
				continue
			channelPath = compTable[inputRow, 'channelPath']
			numericParams = []
			textParams = []
			for par in comp.customPars:
				if not _shouldIncludePar(par):
					continue
				if par.isString:
					textParams.append(par.name)
				else:
					numericParams.append(par.name)
			dat.appendRow([
				comp.path,
				channelPath,
				' '.join(sorted(numericParams)),
				' '.join(sorted(textParams)),
			])

	def _GetComponentInfos(self):
		compTable = self._GetTable(autoInit=False)
		if not compTable:
			return []
		infos = []  # type: List[_ComponentInfo]
		for i in range(1, compTable.numRows):
			comp = op(compTable[i, 'component'])
			if not comp:
				continue
			numericParams = []
			textParams = []
			for par in comp.customPars:
				if not _shouldIncludePar(par):
					continue
				if par.isString or par.isMenu:
					textParams.append(par)
				else:
					numericParams.append(par)
			if not numericParams and not textParams:
				continue
			infos.append(_ComponentInfo(
				comp,
				compTable[i, 'channelPath'].val,
				numericParams,
				textParams,
			))
		return infos

	def _BuildParamTable(self, compInfos: List['_ComponentInfo']):
		paramTable = self.ownerComp.op('set_param_table')  # type: DAT
		paramTable.clear()
		paramTable.appendRow(['channel', 'component', 'param', 'isText', 'initial'])
		for compInfo in compInfos:
			for par in compInfo.numericParams:
				paramTable.appendRow([
					compInfo.channelPath + ':' + par.name,
					compInfo.comp.path,
					par.name,
					0,
					formatValue(par.eval()),
				])
			for par in compInfo.textParams:
				paramTable.appendRow([
					compInfo.channelPath + ':' + par.name,
					compInfo.comp.path,
					par.name,
					1,
					formatValue(par.eval()),
				])

	def _BuildParSelectors(self, compInfos: List['_ComponentInfo']):
		for o in self.ownerComp.ops('getparchop__*', 'getpardat__*', 'getparstate__*'):
			o.destroy()
		for i, compInfo in enumerate(compInfos):
			numericNames = [par.name for par in compInfo.numericParams]
			textNames = [par.name for par in compInfo.textParams]
			renameTo = compInfo.channelPath + ':*'
			if compInfo.numericParams:
				createOP(
					parameterCHOP,
					self.ownerComp,
					'getparchop__{}'.format(i),
					OPAttrs(
						parVals={
							'ops': compInfo.comp.path,
							'parameters': ' '.join(numericNames),
							'renameto': renameTo,
						},
						nodePos=(400, 200 - (i * 150)),
						cloneImmune=True,
					),
				)
			if compInfo.textParams:
				createOP(
					parameterDAT,
					self.ownerComp,
					'getpardat__{}'.format(i),
					OPAttrs(
						parVals={
							'ops': compInfo.comp.path,
							'parameters': ' '.join(textNames),
							'header': False,
							'renameto': renameTo,
						},
						nodePos=(600, 200 - (i * 150)),
						cloneImmune=True,
					),
				)
			createOP(
				parameterDAT,
				self.ownerComp,
				'getparstate__{}'.format(i),
				OPAttrs(
					parVals={
						'ops': compInfo.comp.path,
						'parameters': ' '.join(numericNames + textNames),
						'renameto': renameTo,
						'header': True,
						'name': True,
						'value': False,
						'mode': True,
						'enabled': True,
					},
					nodePos=(800, 200 - (i * 150)),
					cloneImmune=True,
				),
			)

	def RebuildParameters(self):
		compInfos = self._GetComponentInfos()
		self._BuildParamTable(compInfos)
		self._BuildParSelectors(compInfos)

	def _SendMessage(self, name: str, data=None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(name, data, namespace=str(self.par.Messagenamespace)))

	def HandleMessage(self, message: Message):
		if not self.par.Enable:
			return
		namespace = str(self.par.Messagenamespace)
		if namespace and message.namespace != namespace:
			return
		if message.name == CommonMessages.setPar:
			self._SetParVal(channelName=message.data[0], val=message.data[1])

	def _GetParByChannel(self, channelName: str) -> Optional['Par']:
		paramTable = self.ownerComp.op('param_table')  # type: DAT
		compPath = paramTable[channelName, 'component']
		comp = op(compPath) if compPath else None
		if comp is None:
			return None
		parName = paramTable[channelName, 'param']
		par = getattr(comp.par, parName.val, None) if parName else None
		return par

	def _SetParVal(self, channelName: str, val: Any):
		par = self._GetParByChannel(channelName)
		if par is None:
			self._LogEvent('WARNING parameter not found: {}'.format(channelName))
			return
		if par.enable and (par.mode == ParMode.CONSTANT or par.mode == ParMode.BIND):
			par.val = val
		else:
			self._LogEvent('WARNING parameter cannot be set: {} (mode: {}, enable: {})'.format(
				channelName, par.mode, par.enable))

	def SendParVal(self, channelName: str, val: Any):
		self._SendMessage(CommonMessages.parVal, [channelName, val])

	def OnNumericParChannelChange(self, channel: 'Channel', val: float):
		self.SendParVal(channel.name, val)

	def OnTextParCellChange(self, cells: List['Cell']):
		for cell in cells:
			if cell.col == 1:
				self.SendParVal(cell.offset(0, -1).val, cell.val)

def _shouldIncludePar(par: 'Par'):
	if par.readOnly or not par.enable:
		return False
	if par.label.startswith(':') or par.page.name.startswith(':'):
		return False
	if par.isOP:
		return False
	return True

@dataclass
class _ComponentInfo:
	comp: 'COMP'
	channelPath: str
	numericParams: List['Par']
	textParams: List['Par']
