from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import common
from common import loggedmethod

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternChooser(common.ExtensionBase):
	def BuildPatternTable(self, dat: 'DAT', files: 'DAT'):
		dat.clear()
		dat.appendRow(['pattern', 'dataPath', 'thumbPath', 'projectPath'])
		dataDir = Path(self.par.Datafolder.eval())
		patterns = {}  # type: Dict[str, _PatternInfo]
		for row in range(1, files.numRows):
			fileName = files[row, 'name'].val
			relPath = dataDir / files[row, 'relpath'].val
			name, kind = self._ParseFileName(fileName)
			if not name:
				continue
			if name not in patterns:
				patterns[name] = _PatternInfo(name)
			info = patterns[name]  # type: _PatternInfo
			pathStr = str(relPath.as_posix())
			if kind == 'data':
				info.data = pathStr
			elif kind == 'thumb':
				info.thumb = pathStr
			elif kind == 'project':
				info.project = pathStr
		for pattern in patterns.values():
			if not pattern.data:
				continue
			dat.appendRow([pattern.name, pattern.data, pattern.thumb or '', pattern.project or ''])

	@staticmethod
	def _ParseFileName(filePath: str):
		if filePath.endswith('-data.json'):
			return filePath.replace('-data.json', ''), 'data'
		if filePath.endswith('-thumb.png'):
			return filePath.replace('-thumb.png', ''), 'thumb'
		if filePath.endswith('-project.json'):
			return filePath.replace('-project.json', ''), 'project'
		return None, None

	def OnEntryLoadPulse(self, entryComp: 'COMP'):
		patternName = entryComp.par.Patternname.eval()
		self._SelectPattern(patternName)

	@loggedmethod
	def _SelectPattern(self, patternName: str):
		self.par.Selectedpattern = patternName or ''
		patternJsonDat = self.op('load_pattern_json')
		projectJsonDat = self.op('load_project_json')
		patternTable = self.op('pattern_table')
		if not patternName or not patternTable[patternName, 'pattern']:
			patternJsonDat.text = ''
			projectJsonDat.text = ''
		else:
			patternJsonDat.par.loadonstartpulse.pulse()
			if not projectJsonDat.par.file:
				projectJsonDat.text = ''
			else:
				projectJsonDat.par.loadonstartpulse.pulse()

@dataclass
class _PatternInfo:
	name: str
	data: str = None
	thumb: str = None
	project: str = None
