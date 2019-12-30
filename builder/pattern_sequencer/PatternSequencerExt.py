import common
from pm2_settings import PSequenceGenSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PatternSequencer(common.ExtensionBase):
	pass

class _SequenceGenerator(common.LoggableSubComponent):
	def __init__(self, hostObj, seqGenSpec: PSequenceGenSpec, logPrefix: str = None):
		super().__init__(hostObj, logPrefix)
		self.baseName = seqGenSpec

