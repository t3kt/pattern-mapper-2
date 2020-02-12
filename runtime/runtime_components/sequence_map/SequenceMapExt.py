from typing import Union, List

from common import toJson
from pm2_model import PSequence, PSequenceStep, ModelTableWriter
from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SequenceMap(RuntimeComponent, SerializableParams):

	def TEST_WriteSequences(self, outDat: 'DAT'):
		sequence = self._BuildMergedSequence()
		outDat.text = sequence.toJsonStr(minify=False)

	def _ParseSequences(self, seqDat: 'DAT', stepDat: 'DAT') -> List[PSequence]:
		return [
			self._ParseSequence(seqDat, stepDat, i)
			for i in range(1, seqDat.numRows)
		]

	def RebuildSequenceStepTable(self, dat: 'DAT'):
		sequences = self._BuildMergedSequence()
		ModelTableWriter(dat).writeSequenceSteps([sequences])

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

	def _BuildMergedSequence(self):
		seqDat = self.op('selected_sequences')  # type: DAT
		stepDat = self.op('selected_steps')  # type: DAT
		mergeType = self.par.Sequencemergetype.eval()
		sequences = self._ParseSequences(seqDat, stepDat)
		if not sequences:
			return PSequence()
		if len(sequences) == 1:
			return sequences[0]
		if mergeType == 'sequential':
			return self._MergeSequencesSequential(sequences)
		elif mergeType == 'parallel':
			return self._MergeSequencesParallel(sequences)
		else:
			return PSequence()

	@staticmethod
	def _MergeSequencesSequential(sequences: List[PSequence]):
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

	def _MergeSequencesParallel(self, sequences: List[PSequence]):
		# TODO: IMPLEMENT PARALLEL MERGE!
		return PSequence()

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
