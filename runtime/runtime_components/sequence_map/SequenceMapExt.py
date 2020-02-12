from typing import Union, List

from pm2_model import PSequence, PSequenceStep, ModelTableWriter
from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SequenceMap(RuntimeComponent, SerializableParams):

	def _ParseSequences(self) -> List[PSequence]:
		seqDat = self.op('selected_sequences')  # type: DAT
		stepDat = self.op('selected_steps')  # type: DAT
		return [
			self._ParseSequence(seqDat, stepDat, i)
			for i in range(1, seqDat.numRows)
		]

	def BuildSequentialStepTable(self, dat: 'DAT'):
		sequences = self._ParseSequences()
		mergedSequence = self._BuildMergedSequential(sequences)
		ModelTableWriter(dat).writeSequenceSteps([mergedSequence])

	@staticmethod
	def _ParseSequence(seqDat: 'DAT', stepDat: 'DAT', seqRow: Union[str, int]) -> PSequence:
		name = str(seqDat[seqRow, 'sequenceName'] or '')
		return PSequence(
			sequenceName=name,
			steps=list(sorted([
				_parseSequenceStepRow(stepDat, i)
				for i in range(1, stepDat.numRows)
				if stepDat[i, 'sequenceName'] == name
			], key=lambda s: s.sequenceIndex)),
		)

	@staticmethod
	def _BuildMergedSequential(sequences: List[PSequence]):
		mergedSteps = []  # type: List[PSequenceStep]
		sequenceNames = []
		for sequenceIndex, sequence in enumerate(sequences):
			if not sequence.steps:
				continue
			sequenceNames.append(sequence.sequenceName)
			baseIndex = len(mergedSteps)
			# TODO: Handle missing / empty steps properly ...
			for step in sequence.steps:
				mergedSteps.append(PSequenceStep(
					sequenceIndex=baseIndex + step.sequenceIndex,
					shapeIndices=list(step.shapeIndices or []),
					meta={'sequenceName': sequence.sequenceName, 'sequenceIndex': sequenceIndex}
				))
		return PSequence(
			sequenceName='',
			steps=mergedSteps,
			meta={'sequenceNames': ' '.join(sequenceNames)},
		)

def _parseSequenceStepRow(dat: 'DAT', row: Union[str, int]):
	indices = dat[row, 'shapeIndices']
	if not indices:
		indices = []
	else:
		indices = [int(part) for part in indices.val.split(' ')]
	return PSequenceStep(
		sequenceIndex=int(dat[row, 'stepIndex'] or 0),
		shapeIndices=indices,
	)
