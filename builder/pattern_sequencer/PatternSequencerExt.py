import common
from pm2_model import PPattern
from pm2_settings import PSequenceGenSpec, PSettings
from pm2_builder_shared import PatternProcessorBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternSequencer(PatternProcessorBase):
	def _ProcessPattern(
			self,
			pattern: PPattern,
			settings: PSettings) -> PPattern:
		raise NotImplementedError()

class _SequenceGenerator(common.LoggableSubComponent):
	def __init__(self, hostObj, seqGenSpec: PSequenceGenSpec, logPrefix: str = None):
		super().__init__(hostObj, logPrefix)
		self.baseName = seqGenSpec

