import common
import json

from pm2_model import PPattern, PPoint, PShape
from pm2_settings import PPreProcSettings, PSettings

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternPreProcessor(common.ExtensionBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)

	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		inputPatternObj = json.loads(inputPatternJson or '{}')
		pattern = PPattern.fromJsonDict(inputPatternObj)
		settingsJson = self.op('settings_json').text
		settingsObj = json.loads(settingsJson or '{}')
		settings = PSettings.fromJsonDict(settingsObj)
		processor = _PreProcessor(self, settings)
		processor.process(pattern)
		outputPatternJson = json.dumps(pattern.toJsonDict(), indent=None if self.par.Minifyjson else '  ')
		self.op('set_output_pattern_json').text = outputPatternJson

class _PreProcessor(common.LoggableSubComponent):
	def __init__(self, hostObj, settings: PPreProcSettings):
		super().__init__(hostObj, logprefix='PreProc')
		self.settings = settings or PPreProcSettings()
		self.pattern = PPattern()

	def process(self, pattern: PPattern):
		self.pattern = pattern or PPattern()
		pass
