from typing import Optional

from common import ExtensionBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ParameterBindHost(ExtensionBase):
	def Reset(self):
		table = self._GetTable(autoInit=False)
		if not table or table.numRows < 2:
			return
		table.setSize(1, table.numCols)

	def RegisterComponent(self, comp: 'COMP', channelPath: str):
		table = self._GetTable(autoInit=True)
		table.appendRow([comp.path, channelPath])
		self._RebuildParameterTable()

	def _GetTable(self, autoInit=False) -> Optional['DAT']:
		table = self.par.Comptable.eval()
		if table:
			return table
		if autoInit:
			return self._AutoInitTable()

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

	def _RebuildParameterTable(self):
		paramTable = self.op('set_param_table')  # type: DAT
		paramTable.clear()
		paramTable.appendRow(['component', 'channel', 'param', 'isText'])
		compTable = self._GetTable(autoInit=False)
		if not compTable:
			return
		for i in range(1, compTable.numRows):
			comp = self.ownerComp.op(compTable[i, 'component'])
			if not comp:
				continue
			channelPrefix = compTable[i, 'channelPath'].val + ':'
			for par in comp.customPars:
				if par.readOnly or not par.enable:
					continue
				if par.label.startswith(':') or par.page.name.startswith(':'):
					continue
				paramTable.appendRow([
					comp.path,
					channelPrefix + par.name,
					par.name,
					1 if par.isString or par.isMenu else 0,
				])
