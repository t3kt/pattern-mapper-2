import common
from common import loggedmethod
from pathlib import Path
from pm2_settings import PSettings
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternManager(common.ExtensionBase):
	@property
	def _DataDirectory(self):
		return Path(self.par.Datafolder.eval())

	@property
	def _PatternName(self):
		return str(self.par.Pattern)

	@_PatternName.setter
	def _PatternName(self, val):
		self.par.Pattern = val

	@property
	def _PatternDirectory(self):
		name = self._PatternName
		return (self._DataDirectory / name) if name else None

	@loggedmethod
	def ImportSvg(self, sourceSvgPath: str):
		sourceSvgPath = Path(sourceSvgPath)
		self._LoadPattern(sourceSvgPath.stem, copySvgPath=sourceSvgPath)

	@loggedmethod
	def LoadPattern(self, name: str):
		self._LoadPattern(name)

	@loggedmethod
	def _LoadPattern(self, name: str, copySvgPath: Path = None):
		self._PatternName = name
		patternDir = self._PatternDirectory
		if not patternDir.exists():
			patternDir.mkdir(parents=True, exist_ok=True)
		svgDat = self.op('svg')
		svgDat.text = ''
		svgPath = patternDir / (name + '.svg')
		if copySvgPath:
			svgDat.par.file = copySvgPath
			svgDat.par.loadonstartpulse.pulse()
			svgDat.par.file = svgPath
			svgDat.par.write.pulse()
		else:
			svgDat.par.file = svgPath
			svgDat.par.loadonstartpulse.pulse()
		settingsPath = patternDir / 'settings.py'
		settingsDat = self.op('settings')
		settingsDat.par.file = settingsPath
		settingsDat.text = ''
		if settingsPath.exists():
			settingsDat.par.loadonstartpulse.pulse()
		else:
			settingsDat.copy(self.op('settings_template'))

	def _GetSettings(self) -> Optional[PSettings]:
		settingsDat = self.op('settings')
		if not settingsDat.text:
			return None
		m = settingsDat.module
		return m.settings()

	def GetSettingsJson(self):
		settings = self._GetSettings() or PSettings()
		return settings.toJsonStr(minify=self.par.Minifyjson)

	def OnPulse(self, action: str):
		if action == 'Savesettings':
			self.op('settings').par.write.pulse()
		elif action == 'Loadsettings':
			self.op('settings').par.loadonstartpulse.pulse()
