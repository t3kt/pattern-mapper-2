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
		dat.appendRow(['pattern', 'dataPath', 'thumbPath'])
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
			if kind == 'data':
				info.data = str(relPath.as_posix())
			elif kind == 'thumb':
				info.thumb = str(relPath.as_posix())
		for pattern in patterns.values():
			if not pattern.data:
				continue
			dat.appendRow([pattern.name, pattern.data, pattern.thumb or ''])

	@staticmethod
	def _ParseFileName(filePath: str):
		if filePath.endswith('-data.json'):
			return filePath.replace('-data.json', ''), 'data'
		if filePath.endswith('-thumb.png'):
			return filePath.replace('-thumb.png', ''), 'thumb'
		return None, None

	def OnEntryLoadPulse(self, entryComp: 'COMP'):
		patternName = entryComp.par.Patternname.eval()
		self._SelectPattern(patternName)

	@loggedmethod
	def _SelectPattern(self, patternName: str):
		self.par.Selectedpattern = patternName or ''
		jsonDat = self.op('load_pattern_json')
		patternTable = self.op('pattern_table')
		if not patternName or not patternTable[patternName, 'pattern']:
			jsonDat.text = ''
		else:
			jsonDat.par.loadonstartpulse.pulse()

@dataclass
class _PatternInfo:
	name: str
	data: str = None
	thumb: str = None
