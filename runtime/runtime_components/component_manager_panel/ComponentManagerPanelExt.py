from pm2_project import PComponentSpec
from pm2_runtime_shared import RuntimeComponent, SerializableComponentOrCOMP

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentManagerPanel(RuntimeComponent):
	@property
	def _CompTable(self) -> 'DAT':
		return self.op('comp_table')

	@property
	def _TypeTable(self) -> 'DAT':
		return self.op('type_table')

	def OnMarkerReplicate(self, marker: 'COMP'):
		marker.par.display = True
		i = marker.digits
		compTable = self._CompTable
		targetComp = op(compTable[i, 'path'])
		marker.par.Targetop = targetComp
		subLabelParName = str(self.par.Sublabelpar)
		subLabelPar = getattr(targetComp.par, subLabelParName) if subLabelParName else None
		if subLabelPar is None:
			marker.par.Sublabelvisible = False
		else:
			marker.par.Sublabelvisible = True
			marker.par.Sublabeltext = subLabelPar
		typeTable = self._TypeTable
		typeName = compTable[i, 'compType']
		marker.par.Targetcomptype = typeName
		marker.par.Typelabeltext = typeTable[typeName, 'label']
		enableParName = str(self.par.Enablepar)
		if hasattr(targetComp.par, enableParName):
			marker.par.Enabletogglevisible = True
			marker.par.Enable.bindExpr = 'op("{}").par.{}'.format(targetComp.path, enableParName)
		else:
			marker.par.Enabletogglevisible = False
		amountParName = str(self.par.Amountpar)
		if hasattr(targetComp.par, amountParName):
			marker.par.Amountslidervisible = True
			marker.par.Amount.bindExpr = 'op("{}").par.{}'.format(targetComp.path, amountParName)
		else:
			marker.par.Amountslidervisible = False

	def OnMarkerClick(self, sourceComp: 'COMP', eventType: str):
		if sourceComp.par.parentshortcut == 'marker':
			marker = sourceComp
		else:
			marker = sourceComp.parent.marker
		index = marker.digits - 1

		pass
