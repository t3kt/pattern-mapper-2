import json
import os.path

from common import loggedmethod, toJson, mergeDicts, excludeKeys
from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class AppSettings(RuntimeComponent, SerializableParams):
	def __init__(self, ownerComp):
		RuntimeComponent.__init__(self, ownerComp)
		SerializableParams.__init__(self, ownerComp)

	@loggedmethod
	def Initialize(self):
		self.LoadSettings()

	@property
	def _UIWindow(self) -> 'windowCOMP':
		return op.PMUIWindow

	def GetSettingsJson(self):
		uiWindow = self._UIWindow
		vals = mergeDicts(
			self.GetParDict(),
			{
				'uiWindow': {
					'w': uiWindow.contentWidth,
					'h': uiWindow.contentHeight,
					'x': uiWindow.x,
					'y': uiWindow.y,
				}
			})
		return toJson(vals, minify=False)

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
		vals = json.loads(settingsJson or '{}')
		self.SetParDict(excludeKeys(vals, ['uiWindow']))
		uiWindowVals = vals.get('uiWindow') or {}
		uiWindow = self._UIWindow
		if 'x' in uiWindowVals:
			uiWindow.par.winoffsetx = uiWindowVals['x']
		if 'y' in uiWindowVals:
			uiWindow.par.winoffsety = uiWindowVals['y']
		if 'w' in uiWindowVals:
			uiWindow.par.winw = uiWindowVals['w']
		if 'h' in uiWindowVals:
			uiWindow.par.winh = uiWindowVals['h']
