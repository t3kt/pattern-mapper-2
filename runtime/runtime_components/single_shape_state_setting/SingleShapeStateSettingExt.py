from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SingleShapeStateSetting(RuntimeComponent, SerializableParams):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
