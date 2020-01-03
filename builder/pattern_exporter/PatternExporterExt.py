import common
from common import loggedmethod
from pm2_model import PPattern
from pathlib import Path

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternExporter(common.ExtensionBase):
	@loggedmethod
	def ExportPattern(self):
		inputPatternJsonDat = self.op('input_pattern_json')
		inputPatternJson = inputPatternJsonDat.text
		if not inputPatternJson:
			self.ownerComp.addWarning('No pattern loaded')
			return
		pattern = PPattern.parseJsonStr(inputPatternJson)
		outputPatternJson = pattern.toJsonStr(minify=self.par.Minifyjson.eval())
		outputPatternJsonDat = self.op('set_output_pattern_json')  # type: DAT
		outputPatternJsonDat.text = outputPatternJson
		pathsDat = self.op('paths')
		patternDir = Path(pathsDat['dir', 1].val)
		buildDir = patternDir / 'build'
		if not buildDir.exists():
			buildDir.mkdir(parents=True, exist_ok=True)
		patternName = patternDir.name
		jsonPath = buildDir / '{}-data.json'.format(patternName)
		outputPatternJsonDat.save(str(jsonPath.as_posix()))
		ui.status = 'Wrote pattern data to {!r}'.format(str(jsonPath.resolve()))
		thumbPath = buildDir / '{}-thumb.png'.format(patternName)
		thumbTop = self.op('thumb_image')  # type: TOP
		thumbTop.save(str(thumbPath.as_posix()))
