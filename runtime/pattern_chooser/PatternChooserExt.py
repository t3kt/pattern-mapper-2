from dataclasses import dataclass
from pathlib import Path

from common import loggedmethod, simpleloggedmethod
from pm2_project import PProject
from pm2_runtime_shared import RuntimeComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternChooser(RuntimeComponent):
	def BuildPatternTable(self, dat: 'DAT', files: 'DAT'):
		dat.clear()
		dat.appendRow(['pattern', 'dir', 'dataPath', 'thumbPath', 'projectPath'])
		dataDir = Path(self.par.Datafolder.eval())
		names = list(sorted([c.val for c in files.col('name')[1:]]))
		for name in names:
			patternDir = dataDir / name
			dat.appendRow([
				name,
				str(patternDir.as_posix()),
				str((patternDir / 'build' / '{}-data.json'.format(name)).as_posix()),
				str((patternDir / 'build' / '{}-thumb.png'.format(name)).as_posix()),
				str((patternDir / '{}-project.json'.format(name)).as_posix()),
			])

	@loggedmethod
	def OnLoadButtonClick(self):
		radios = self.op('patterns_radio')
		patternIndex = int(radios.par.Value0)
		patternTable = self.op('pattern_table')
		patternName = patternTable[patternIndex + 1, 'pattern'].val
		self.SelectPattern(patternName)

	@loggedmethod
	def SelectPattern(self, patternName: str):
		self.par.Selectedpattern = patternName or ''
		patternJsonDat = self.op('load_pattern_json')
		projectJsonDat = self.op('load_project_json')
		patternTable = self.op('pattern_table')
		patternJsonDat.par.file = ''
		projectJsonDat.par.file = ''
		patternJsonDat.text = ''
		projectJsonDat.text = ''
		if patternName and patternTable[patternName, 'pattern']:
			patternPath = Path(patternTable[patternName, 'dataPath'].val)
			if patternPath.exists():
				patternJsonDat.par.file = str(patternPath.as_posix())
				patternJsonDat.par.loadonstartpulse.pulse()
			projectPath = Path(patternTable[patternName, 'projectPath'].val)
			if projectPath.exists():
				projectJsonDat.par.file = str(projectPath.as_posix())
				projectJsonDat.par.loadonstartpulse.pulse()
			self._RuntimeApp.OnChoosePattern()

	@simpleloggedmethod
	def SaveProject(self, project: PProject):
		projectJson = project.toJsonStr(minify=False)
		projectJsonDat = self.op('load_project_json')
		projectJsonDat.text = projectJson
		projectJsonDat.par.writepulse.pulse()

@dataclass
class _PatternInfo:
	name: str
	data: str = None
	thumb: str = None
	project: str = None
