from dataclasses import dataclass
from typing import Union, List, Dict

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

	def BuildSequenceStepTable(self, dat: 'DAT'):
		mergedSequence = self._BuildMergedSequence()
		ModelTableWriter(dat).writeSequenceSteps([mergedSequence], includeMeta=True, includeSequenceName=False)

	def BuildShapeSequenceStepMaskTable(self, dat: 'DAT', shapeCount: int):
		mergedSequence = self._BuildMergedSequence()
		ModelTableWriter(dat).writeShapeSequenceStepMaskTable(
			mergedSequence,
			shapeCount=shapeCount)

	@staticmethod
	def _ParseSequence(seqDat: 'DAT', stepDat: 'DAT', seqRow: Union[str, int]) -> PSequence:
		name = str(seqDat[seqRow, 'sequenceName'] or '')
		stepsByIndex = {}
		maxIndex = 0
		for i in range(1, stepDat.numRows):
			if stepDat[i, 'sequenceName'] != name:
				continue
			step = _parseSequenceStepRow(stepDat, i)
			stepsByIndex[step.sequenceIndex] = step
			maxIndex = max(maxIndex, step.sequenceIndex)
		# make sure there's a step for each sequence index even if there aren't any shapes in them
		paddedSteps = [
			stepsByIndex.get(i) if i in stepsByIndex else PSequenceStep(sequenceIndex=i)
			for i in range(maxIndex + 1)
		]
		return PSequence(
			sequenceName=name,
			steps=paddedSteps,
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

	# def BuildParallelStepLookupChop(
	# 		self,
	# 		chop: 'scriptCHOP'):
	# 	chop.clear()
	# 	sequences = self._ParseSequences()
	# 	if not sequences:
	# 		pass
	# 	# alignstart alignend
	# 	# stretchfirst stretchlong stretchshort - NOT CURRENTLY SUPPORTED
	# 	alignMode = self.par.Sequencealignmode.eval()
	# 	if alignMode.startswith('align'):
	# 		self._BuildParallelStepLookupAligned(chop, sequences, alignMode)
	# 	elif alignMode.startswith('stretch'):
	# 		raise NotImplementedError('stretch alignment not supported')
	#
	# @staticmethod
	# def _BuildParallelStepLookupAligned(chop: 'scriptCHOP', sequences: List[PSequence], mode: str):
	# 	totalStepCount = max([len(seq.steps) for seq in sequences])
	# 	chop.numSamples = totalStepCount
	# 	usingStart = mode == 'alignstart'
	# 	for sequence in sequences:
	# 		chan = chop.appendChan('step_' + sequence.sequenceName)
	# 		if usingStart:
	# 			# seq 1:  0  1  2  3  4  5  6  7
	# 			# seq 2:  0  1  2  3  4  x  x  x
	# 			for i in range(totalStepCount):
	# 				if i < len(sequence.steps):
	# 					chan[i] = i
	# 				else:
	# 					chan[i] = - 1
	# 		else:
	# 			# seq 1:  0  1  2  3  4  5  6  7
	# 			# seq 2:  x  x  x  0  1  2  3  4
	# 			startIndex = totalStepCount - len(sequence.steps)
	# 			for i in range(len(sequence.steps)):
	# 				pass
	# 			for step in sequence.steps:
	# 				chan[step.sequenceIndex + startIndex] = step.sequenceIndex


	def _BuildMergedSequence(self):
		sequences = self._ParseSequences()
		if self.par.Sequencemergetype == 'sequential':
			return self._BuildMergedSequential(sequences)
		else:
			return self._BuildMergedParallelAligned(sequences)

	def _BuildMergedParallelAligned(self, sequences: List[PSequence]):
		if not sequences:
			return PSequence()
		totalStepCount = max([len(seq.steps) for seq in sequences])
		alignMode = self.par.Sequencealignmode.eval()
		usingStart = alignMode == 'alignstart'
		stepListsByIndex = {}  # type: Dict[int, List[_StepWithName]]
		for sequence in sequences:
			if usingStart:
				indexOffset = 0
			else:
				indexOffset = totalStepCount - len(sequence.steps)
			for step in sequence.steps:
				newIndex = indexOffset + step.sequenceIndex
				if newIndex not in stepListsByIndex:
					stepListsByIndex[newIndex] = []
				stepListsByIndex[newIndex].append(_StepWithName(sequence.sequenceName, step))
		mergedSteps = []  # type: List[PSequenceStep]
		for index in range(totalStepCount):
			shapeIndices = set()
			partNames = []
			for step in stepListsByIndex.get(index) or []:
				shapeIndices.update(step.step.shapeIndices)
				partNames.append(f'{step.sequenceName}.{step.step.sequenceIndex}')
			mergedSteps.append(PSequenceStep(
				sequenceIndex=index,
				shapeIndices=list(sorted(shapeIndices)),
				meta={'steps': partNames},
			))
		return PSequence(
			steps=mergedSteps,
			meta={'sequences': [sequence.sequenceName for sequence in sequences]}
		)

@dataclass
class _StepWithName:
	sequenceName: str
	step: PSequenceStep

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
