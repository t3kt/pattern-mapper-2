import json
import os.path

from common import loggedmethod, toJson
from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class AppSettings(RuntimeComponent, SerializableParams):
	def __init__(self, ownerComp):
		RuntimeComponent.__init__(self, ownerComp)
		SerializableParams.__init__(self, ownerComp)

	def GetSettingsJson(self):
		return toJson(self.GetParDict(), minify=False)

	@loggedmethod
	def SaveSettings(self):
		self.op('settings_fileout').par.write.pulse()

	@loggedmethod
	def LoadSettings(self):
		settingsJson = None
		if self.par.Settingsfile and os.path.exists(self.par.Settingsfile.eval()):
			dat = self.op('settings_filein')
			dat.par.refreshpulse.pulse()
			settingsJson = dat.text
		settingsDict = json.loads(settingsJson or '{}')
		self.SetParDict(settingsDict)
