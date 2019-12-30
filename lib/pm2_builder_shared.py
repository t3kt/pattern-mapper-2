from abc import ABC, abstractmethod
import common
from common import loggedmethod
from pm2_model import PPattern
from pm2_settings import PSettings


class PatternProcessorBase(common.ExtensionBase, ABC):
	@loggedmethod
	def ProcessPattern(self):
		inputPatternJson = self.op('input_pattern_json').text
		pattern = PPattern.parseJsonStr(inputPatternJson)
		settingsJson = self.op('settings_json').text
		settings = PSettings.parseJsonStr(settingsJson)
		pattern = self._ProcessPattern(pattern, settings)
		outputPatternJson = pattern.toJsonStr(minify=self.par.Minifyjson)
		self.op('set_output_pattern_json').text = outputPatternJson

	@abstractmethod
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		pass
