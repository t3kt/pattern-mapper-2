from typing import Union, List

from common import toJson
from pm2_model import PSequence, PSequenceStep
from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SequenceMap(RuntimeComponent, SerializableParams):

	def TEST_WriteSequences(self, outDat: 'DAT', seqDat: 'DAT', stepsDat: 'DAT'):
		sequences = self._ParseSequences(seqDat, stepsDat)
		outDat.text = toJson(PSequence.toJsonDicts(sequences), minify=False)

	def _ParseSequences(self, seqDat: 'DAT', stepsDat: 'DAT') -> List[PSequence]:
		return [
			self._ParseSequence(seqDat, stepsDat, i)
			for i in range(1, seqDat.numRows)
		]

	@staticmethod
	def _ParseSequence(seqDat: 'DAT', stepsDat: 'DAT', seqRow: Union[str, int]) -> PSequence:
		name = str(seqDat[seqRow, 'sequenceName'] or '')
		return PSequence(
			sequenceName=name,
			steps=list(sorted([
				_parseSequenceStepRow(stepsDat, i)
				for i in range(1, stepsDat.numRows)
				if stepsDat[i, 'sequenceName'] == name
			], key=lambda s: s.sequenceIndex)),
		)

	def _BuildMergedSequence(self, seqDat: 'DAT', stepsDat: 'DAT'):
		mergeType = self.par.Sequencemergetype.eval()
		sequences = self._ParseSequences(seqDat, stepsDat)
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
			steps=mergedSteps,
			meta={'sequenceNames': ' '.join(sequenceNames)},
		)

	def _MergeSequencesParallel(self, sequences: List[PSequence]):
		# TODO: IMPLEMENT PARALLEL MERGE!
		return PSequence()

def _parseSequenceStepRow(dat: 'DAT', row: Union[str, int]):
	return PSequenceStep(
		sequenceIndex=int(dat[row, 'stepIndex'] or 0),
		shapeIndices=list(map(int, str(dat[row, 'shapeIndices'] or '').split(' '))) if dat[row, 'shapeIndices'] else [],
	)
