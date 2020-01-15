from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ExternalSources(RuntimeComponent):
	def BuildSyphonSpoutSourceTable(self, dat: 'DAT'):
		_fillTableFromMenuPar(
			dat,
			self.op('syphonspoutin').par.sendername,
			typeName='syphonspout',
			excludePrefix='__')

	def BuildDeviceTable(self, dat: 'DAT'):
		_fillTableFromMenuPar(
			dat,
			self.op('videodevin').par.device,
			typeName='device')

	@staticmethod
	def BuildNdiSourceTable(dat: 'DAT', sourcesDat: 'DAT'):
		dat.clear()
		dat.appendRow(['name', 'label', 'type'])
		for name in sourcesDat.col('sourceName')[1:]:
			dat.appendRow([name, name, 'ndi'])

def _fillTableFromMenuPar(dat: 'DAT', par: 'Par', typeName: str, excludePrefix: str = None):
	dat.clear()
	dat.appendRow(['name', 'label', 'type'])
	for name, label in zip(par.menuNames, par.menuLabels):
		if excludePrefix and name.startswith(excludePrefix):
			continue
		dat.appendRow([name, label, typeName])
