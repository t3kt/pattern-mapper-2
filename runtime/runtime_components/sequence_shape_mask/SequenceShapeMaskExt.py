import common

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SequenceShapeMask(common.ExtensionBase):
	# @common.loggedmethod
	def BuildStepMaskTable(self, dat: 'DAT', stepsDat: 'DAT', stepCount: int, shapeCount: int):
		dat.clear()
		for stepIndex in range(stepCount):
			cell = stepsDat[str(stepIndex), 'shapeIndices']
			# self._LogEvent('step {} cell: {!r}'.format(stepIndex, cell))
			if cell and cell.val:
				shapeIndices = set(map(int, cell.val.split(' ')))
				dat.appendRow([1 if shapeIndex in shapeIndices else 0 for shapeIndex in range(shapeCount)])
			else:
				dat.appendRow([0] * shapeCount)

