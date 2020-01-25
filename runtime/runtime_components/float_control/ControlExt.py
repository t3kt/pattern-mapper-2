from pm2_runtime_shared import RuntimeComponent, SerializableComponent

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class FloatControl(RuntimeComponent, SerializableComponent):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
